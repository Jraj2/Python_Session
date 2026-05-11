"""
scrape_eu_category_jobs.py

Scrapes Sales and Project Manager jobs from dailyremote.com, filters for
European locations, and saves results to .tmp/eu_jobs_raw.json.

Usage:
    python tools/scrape_eu_category_jobs.py [--target N] [--max-pages N]

Defaults:
    --target    500  (stop when this many EU jobs are collected)
    --max-pages 250  (hard credit-usage cap across all categories)

Output:
    .tmp/eu_jobs_raw.json  — array of job objects with fields:
        title, company, location, job_type, category, source_category,
        salary, experience, date_posted, url

Location filter:
    Keeps jobs whose location tag contains any European country name or
    region keyword. Excludes US-only, Canada-only, APAC, Worldwide, etc.
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
TMP_DIR = BASE_DIR / ".tmp"
OUTPUT_FILE = TMP_DIR / "eu_jobs_raw.json"

# ── Categories to scrape ────────────────────────────────────────────────────
CATEGORIES = [
    {
        "name": "Project Manager",
        "base_url": "https://dailyremote.com/remote-project-manager-jobs",
    },
    {
        "name": "Sales",
        "base_url": "https://dailyremote.com/remote-sales-jobs",
    },
]

# ── European location keywords (case-insensitive substring match) ────────────
EUROPE_KEYWORDS = {
    "europe", "european", "emea", "eu ",
    # British Isles
    "uk", "united kingdom", "england", "scotland", "wales", "northern ireland",
    "ireland",
    # Western Europe
    "germany", "deutschland", "france", "spain", "italy", "italia", "portugal",
    "netherlands", "holland", "belgium", "luxembourg", "austria", "switzerland",
    "liechtenstein", "monaco", "andorra", "san marino",
    # Nordics
    "sweden", "norway", "denmark", "finland", "iceland",
    # Eastern/Central Europe
    "poland", "czech", "slovakia", "hungary", "romania", "bulgaria",
    "slovenia", "croatia", "serbia", "bosnia", "montenegro", "north macedonia",
    "albania", "moldova", "ukraine", "belarus", "estonia", "latvia", "lithuania",
    # Southern Europe
    "greece", "cyprus", "malta",
    # Other
    "georgia", "armenia", "azerbaijan",
}


def is_european(location_text: str) -> bool:
    lower = location_text.lower()
    return any(kw in lower for kw in EUROPE_KEYWORDS)


# ── HTML parsing ─────────────────────────────────────────────────────────────
_JOB_TYPES = {"full time", "part time", "contract", "freelance", "internship",
              "full-time", "part-time"}
_DATE_RE = re.compile(
    r'\b(ago|today|yesterday|\d+\s*(min|hour|day|week|month))', re.IGNORECASE
)


def _classify_span(text: str) -> str:
    lower = text.lower()
    if lower in _JOB_TYPES or any(jt in lower for jt in _JOB_TYPES):
        return "job_type"
    if _DATE_RE.search(text):
        return "date_posted"
    return "company"


def _clean_emoji(text: str) -> str:
    return re.sub(r'^[\U00010000-\U0010ffff☀-➿\s]+', '', text).strip()


def parse_card(card, source_category: str):
    h2 = card.find("h2", class_="job-position")
    a = h2.find("a") if h2 else None
    if not a:
        return None
    title = a.get_text(strip=True)
    url = a.get("href", "")

    # Company / job_type / date_posted
    company = job_type = date_posted = ""
    company_div = card.find("div", class_="company-name")
    if company_div:
        spans = [
            s.get_text(strip=True)
            for s in company_div.find_all("span", recursive=False)
            if s.get_text(strip=True) not in ("", "·")
        ]
        for span_text in spans:
            kind = _classify_span(span_text)
            if kind == "job_type" and not job_type:
                job_type = span_text.strip()
            elif kind == "date_posted" and not date_posted:
                date_posted = span_text.strip()
            elif kind == "company" and not company:
                company = span_text.strip()

    # card-tags: 🌎 location, 💵 salary, ⭐ experience
    location = salary = experience = ""
    for tag in card.find_all("span", class_="card-tag"):
        text = tag.get_text(strip=True)
        if any(e in text for e in ["\U0001f30e", "\U0001f30d", "\U0001f30f", "🌎", "🌍"]):
            location = _clean_emoji(text)
        elif "💵" in text:
            salary = _clean_emoji(text)
        elif "⭐" in text:
            experience = _clean_emoji(text).lstrip("⭐ ").strip()

    # Category tag
    category = ""
    cat_tag = card.find("span", class_="category-tag")
    if cat_tag:
        cat_a = cat_tag.find("a")
        if cat_a:
            category = _clean_emoji(cat_a.get_text(strip=True))

    return {
        "title":           title,
        "company":         company,
        "location":        location,
        "job_type":        job_type,
        "category":        category,
        "source_category": source_category,
        "salary":          salary,
        "experience":      experience,
        "date_posted":     date_posted,
        "url":             url,
    }


def page_url(base_url: str, page_num: int) -> str:
    if page_num == 1:
        return base_url
    return f"{base_url}/?page={page_num}"


def scrape_page(app: FirecrawlApp, url: str, source_category: str) -> list:
    try:
        result = app.scrape(url, formats=["html"])
        html = result.html if hasattr(result, "html") else ""
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("article", class_="card")
        jobs = []
        for card in cards:
            job = parse_card(card, source_category)
            if job:
                jobs.append(job)
        return jobs
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Sales + PM jobs for Europe"
    )
    parser.add_argument("--target", type=int, default=500,
                        help="Stop after collecting this many EU jobs (default 500)")
    parser.add_argument("--max-pages", type=int, default=250,
                        help="Hard cap on total pages scraped (default 250)")
    args = parser.parse_args()

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("ERROR: FIRECRAWL_API_KEY not found in .env", file=sys.stderr)
        sys.exit(1)

    TMP_DIR.mkdir(exist_ok=True)
    app = FirecrawlApp(api_key=api_key)

    all_eu_jobs: list = []
    seen_urls: set = set()
    total_pages_scraped = 0

    print(f"Target: {args.target} European jobs across "
          f"{', '.join(c['name'] for c in CATEGORIES)}")
    print(f"Max pages cap: {args.max_pages}")
    print()

    # Round-robin across categories until target reached
    page_counters = {c["name"]: 1 for c in CATEGORIES}
    category_exhausted = {c["name"]: False for c in CATEGORIES}

    while len(all_eu_jobs) < args.target and total_pages_scraped < args.max_pages:
        made_progress = False

        for cat in CATEGORIES:
            if len(all_eu_jobs) >= args.target:
                break
            if total_pages_scraped >= args.max_pages:
                break
            if category_exhausted[cat["name"]]:
                continue

            pg = page_counters[cat["name"]]
            url = page_url(cat["base_url"], pg)
            print(f"  [{cat['name']:18}] page {pg:3d} | {url}", end=" ... ", flush=True)

            jobs = scrape_page(app, url, cat["name"])
            total_pages_scraped += 1

            if not jobs:
                print(f"0 results — {cat['name']} exhausted.")
                category_exhausted[cat["name"]] = True
                continue

            # Filter for European locations and deduplicate
            eu_new = 0
            for job in jobs:
                if job["url"] in seen_urls:
                    continue
                if is_european(job["location"]):
                    seen_urls.add(job["url"])
                    all_eu_jobs.append(job)
                    eu_new += 1

            eu_rate = int(100 * eu_new / len(jobs)) if jobs else 0
            print(f"{eu_new} EU / {len(jobs)} total ({eu_rate}%) | "
                  f"running EU total: {len(all_eu_jobs)}")

            page_counters[cat["name"]] += 1
            made_progress = True

            if pg < page_counters[cat["name"]]:
                time.sleep(0.8)

        if not made_progress:
            print("All categories exhausted — stopping.")
            break

    # Save
    OUTPUT_FILE.write_text(
        json.dumps(all_eu_jobs, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print()
    print("-" * 60)
    print(f"Done. {len(all_eu_jobs)} EU jobs saved to {OUTPUT_FILE}")
    print(f"Total pages scraped: {total_pages_scraped}")

    # Category breakdown
    from collections import Counter
    cats = Counter(j["source_category"] for j in all_eu_jobs)
    for cat_name, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat_name:25}: {count} jobs")


if __name__ == "__main__":
    main()
