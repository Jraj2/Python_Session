"""
scrape_dentist_leads.py

Scrapes US dentist listings from YellowPages.com by state and saves a
structured lead list to .tmp/dentist_leads_raw.json.

Usage:
    python tools/scrape_dentist_leads.py [--target N] [--pages-per-state N]

Defaults:
    --target           1000  (stop after this many leads total)
    --pages-per-state  4     (max pages to scrape per state, ~30 leads/page)

Output:
    .tmp/dentist_leads_raw.json  — array of lead objects:
        practice_name, phone, street_address, city, state, zip_code,
        specialties, website, rating, review_count, yp_url
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
TMP_DIR  = BASE_DIR / ".tmp"
OUTPUT_FILE = TMP_DIR / "dentist_leads_raw.json"

# Top 10 most populous US states
STATES = [
    ("California",      "CA"),
    ("Texas",           "TX"),
    ("Florida",         "FL"),
    ("New York",        "NY"),
    ("Pennsylvania",    "PA"),
    ("Illinois",        "IL"),
    ("Ohio",            "OH"),
    ("Georgia",         "GA"),
    ("North Carolina",  "NC"),
    ("Michigan",        "MI"),
]

# Rating class → numeric value
RATING_MAP = {
    "one": 1.0, "one-half": 1.5,
    "two": 2.0, "two-half": 2.5,
    "three": 3.0, "three-half": 3.5,
    "four": 4.0, "four-half": 4.5,
    "five": 5.0,
}


def yp_url(state_name: str, page: int) -> str:
    state_slug = state_name.replace(" ", "+")
    base = f"https://www.yellowpages.com/search?search_terms=dentist&geo_location_terms={state_slug}"
    return base if page == 1 else f"{base}&page={page}"


def parse_rating(result_div) -> str:
    """Extract star rating from result-rating CSS class names."""
    rating_div = result_div.select_one("div.result-rating")
    if not rating_div:
        return ""
    classes = " ".join(rating_div.get("class", []))
    for key, val in sorted(RATING_MAP.items(), key=lambda x: -len(x[0])):
        if key in classes:
            return str(val)
    # Fallback: try data-analytics on parent div.result
    try:
        import json as _json
        analytics = _json.loads(result_div.get("data-analytics", "{}"))
        rate = analytics.get("rate")
        if rate:
            return str(rate)
    except Exception:
        pass
    return ""


def parse_review_count(result_div) -> str:
    count_span = result_div.select_one("span.count")
    if not count_span:
        return ""
    text = count_span.get_text(strip=True)
    return re.sub(r"[()]+", "", text).strip()


def parse_result(div, state_abbr: str) -> dict:
    # Practice name
    name_a = div.select_one("a.business-name")
    practice_name = ""
    yp_link = ""
    if name_a:
        span = name_a.find("span")
        practice_name = span.get_text(strip=True) if span else name_a.get_text(strip=True)
        # Strip leading number and period (e.g. "1. Aspen Dental")
        practice_name = re.sub(r"^\d+\.\s*", "", practice_name).strip()
        yp_link = name_a.get("href", "")
        if yp_link and not yp_link.startswith("http"):
            yp_link = "https://www.yellowpages.com" + yp_link

    # Phone
    phone_div = div.select_one("div.phones.phone.primary")
    phone = phone_div.get_text(strip=True) if phone_div else ""

    # Address
    street_div = div.select_one("div.street-address")
    street = street_div.get_text(strip=True) if street_div else ""

    locality_div = div.select_one("div.locality")
    city = state_code = zip_code = ""
    if locality_div:
        raw = locality_div.get_text(strip=True)
        # Typical format: "Modesto, CA 95356"
        m = re.match(r"^(.+),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)?$", raw)
        if m:
            city      = m.group(1).strip()
            state_code = m.group(2)
            zip_code  = (m.group(3) or "").strip()
        else:
            city = raw

    if not state_code:
        state_code = state_abbr

    # Website
    website_a = div.select_one("a.track-visit-website")
    website = ""
    if website_a:
        # Prefer the dku (destination URL) from data-analytics over the href
        try:
            import json as _json
            analytics = _json.loads(website_a.get("data-analytics", "{}"))
            website = analytics.get("dku") or analytics.get("LOC") or ""
        except Exception:
            pass
        if not website:
            website = website_a.get("href", "")
        # Strip tracking params
        website = re.sub(r"[?&]utm_[^&]*", "", website).rstrip("?&")

    # Specialties / categories
    cats = [a.get_text(strip=True) for a in div.select("div.categories a")]
    specialties = ", ".join(cats)

    # Rating and reviews
    rating = parse_rating(div)
    review_count = parse_review_count(div)

    return {
        "practice_name":  practice_name,
        "phone":          phone,
        "street_address": street,
        "city":           city,
        "state":          state_code,
        "zip_code":       zip_code,
        "specialties":    specialties,
        "website":        website,
        "rating":         rating,
        "review_count":   review_count,
        "yp_url":         yp_link,
    }


def scrape_state_page(app: FirecrawlApp, state_name: str, state_abbr: str,
                      page: int) -> list:
    url = yp_url(state_name, page)
    try:
        result = app.scrape(url, formats=["html"])
        html = result.html if hasattr(result, "html") else ""
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        divs = soup.select("div.result")
        leads = []
        for d in divs:
            lead = parse_result(d, state_abbr)
            if lead["practice_name"] and lead["phone"]:
                leads.append(lead)
        return leads
    except Exception as e:
        print(f"    ERROR: {e}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(description="Scrape US dentist leads from YellowPages")
    parser.add_argument("--target",          type=int, default=1000,
                        help="Total leads to collect (default 1000)")
    parser.add_argument("--pages-per-state", type=int, default=4,
                        help="Max pages per state (default 4, ~120 leads/state)")
    args = parser.parse_args()

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("ERROR: FIRECRAWL_API_KEY not found in .env", file=sys.stderr)
        sys.exit(1)

    TMP_DIR.mkdir(exist_ok=True)
    app = FirecrawlApp(api_key=api_key)

    all_leads: list = []
    seen_phones: set = set()
    total_pages = 0

    print(f"Target: {args.target} dentist leads across {len(STATES)} states")
    print(f"Max pages per state: {args.pages_per_state}  "
          f"(est. max {len(STATES) * args.pages_per_state * 30} raw results)\n")

    for state_name, state_abbr in STATES:
        if len(all_leads) >= args.target:
            break

        state_leads = 0
        print(f"  [{state_abbr}] {state_name}")

        for page in range(1, args.pages_per_state + 1):
            if len(all_leads) >= args.target:
                break

            print(f"    page {page} ...", end=" ", flush=True)
            leads = scrape_state_page(app, state_name, state_abbr, page)
            total_pages += 1

            if not leads:
                print("no results — done with state.")
                break

            new = 0
            for lead in leads:
                # Deduplicate by phone number
                key = re.sub(r"\D", "", lead["phone"])
                if key and key not in seen_phones:
                    seen_phones.add(key)
                    all_leads.append(lead)
                    state_leads += 1
                    new += 1

            print(f"{new} new leads (state total: {state_leads}, overall: {len(all_leads)})")

            if page < args.pages_per_state:
                time.sleep(1.2)

        print()

    OUTPUT_FILE.write_text(
        json.dumps(all_leads, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("-" * 60)
    print(f"Done. {len(all_leads)} leads saved to {OUTPUT_FILE}")
    print(f"Total pages scraped: {total_pages}")
    print()

    from collections import Counter
    state_counts = Counter(j["state"] for j in all_leads)
    print("Leads by state:")
    for st, cnt in sorted(state_counts.items(), key=lambda x: -x[1]):
        print(f"  {st}: {cnt}")


if __name__ == "__main__":
    main()
