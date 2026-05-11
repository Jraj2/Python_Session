"""
scrape_job_listings.py

Scrapes job listings from dailyremote.com using Firecrawl (HTML mode) +
BeautifulSoup parsing. Saves results to .tmp/jobs_raw.json.

Usage:
    python tools/scrape_job_listings.py [--pages N]

Inputs:
    FIRECRAWL_API_KEY in .env
    --pages N  (default: 7 — yields ~200 jobs at ~30/page)

Output:
    .tmp/jobs_raw.json  — array of job objects with fields:
        title, company, location, job_type, category, salary, experience,
        date_posted, url
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
OUTPUT_FILE = TMP_DIR / "jobs_raw.json"


def page_url(page_num: int) -> str:
    if page_num == 1:
        return "https://dailyremote.com/remote-jobs/"
    return f"https://dailyremote.com/remote-jobs/?page={page_num}"


def clean_emoji(text: str) -> str:
    """Strip leading emoji and whitespace from a tag string."""
    return re.sub(r'^[\U00010000-\U0010ffff☀-➿\s]+', '', text).strip()


_JOB_TYPES = {"full time", "part time", "contract", "freelance", "internship",
              "full-time", "part-time"}
_DATE_PATTERNS = re.compile(
    r'\b(ago|today|yesterday|\d+\s*(min|hour|day|week|month))',
    re.IGNORECASE
)


def _classify_span(text: str) -> str:
    """Return 'job_type', 'date_posted', or 'company' based on content."""
    lower = text.lower()
    if lower in _JOB_TYPES or any(jt in lower for jt in _JOB_TYPES):
        return "job_type"
    if _DATE_PATTERNS.search(text):
        return "date_posted"
    return "company"


def parse_card(card) -> dict:
    # Title and URL
    h2 = card.find("h2", class_="job-position")
    a = h2.find("a") if h2 else None
    title = a.get_text(strip=True) if a else ""
    url = a.get("href", "") if a else ""

    # Company, job_type, date_posted from .company-name spans
    # Format varies: may be [company · job_type · date] or [job_type · date]
    company_div = card.find("div", class_="company-name")
    company = job_type = date_posted = ""
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

    # card-tag spans: 🌎 location, 💵 salary, ⭐ experience
    location = salary = experience = ""
    for tag in card.find_all("span", class_="card-tag"):
        text = tag.get_text(strip=True)
        if "\U0001f30e" in text or "\U0001f30d" in text or "🌎" in text:
            location = clean_emoji(text)
        elif "💵" in text:
            salary = clean_emoji(text)
        elif "⭐" in text or "⭐" in text:
            experience = clean_emoji(text).lstrip("⭐ ").strip()

    # Category from .category-tag a
    category = ""
    cat_tag = card.find("span", class_="category-tag")
    if cat_tag:
        cat_a = cat_tag.find("a")
        if cat_a:
            category = clean_emoji(cat_a.get_text(strip=True))

    return {
        "title":        title,
        "company":      company,
        "location":     location,
        "job_type":     job_type,
        "category":     category,
        "salary":       salary,
        "experience":   experience,
        "date_posted":  date_posted,
        "url":          url,
    }


def scrape_page(app: FirecrawlApp, url: str) -> list:
    try:
        result = app.scrape(url, formats=["html"])
        html = result.html if hasattr(result, "html") else ""
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("article", class_="card")
        return [parse_card(c) for c in cards if c.find("h2", class_="job-position")]
    except Exception as e:
        print(f"  ERROR scraping {url}: {e}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(description="Scrape DailyRemote job listings")
    parser.add_argument("--pages", type=int, default=7,
                        help="Number of pages to scrape (default: 7 ≈ 200 jobs)")
    args = parser.parse_args()

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("ERROR: FIRECRAWL_API_KEY not found in .env", file=sys.stderr)
        sys.exit(1)

    TMP_DIR.mkdir(exist_ok=True)

    app = FirecrawlApp(api_key=api_key)
    all_jobs: list = []
    seen_urls: set = set()

    print(f"Scraping up to {args.pages} pages from dailyremote.com...")

    for page_num in range(1, args.pages + 1):
        url = page_url(page_num)
        print(f"  Page {page_num:2d}: {url}", end=" ... ", flush=True)

        jobs = scrape_page(app, url)

        if not jobs:
            print("0 jobs — stopping early.")
            break

        new_jobs = [j for j in jobs if j["url"] not in seen_urls]
        for j in new_jobs:
            if j["url"]:
                seen_urls.add(j["url"])

        all_jobs.extend(new_jobs)
        print(f"{len(new_jobs)} jobs (total: {len(all_jobs)})")

        if page_num < args.pages:
            time.sleep(1)

    OUTPUT_FILE.write_text(
        json.dumps(all_jobs, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nDone. {len(all_jobs)} jobs saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
