"""
Scrape customer reviews for a company from G2, Capterra, and Trustpilot.
Usage: python fetch_reviews.py --company <name> [--g2-slug <slug>]
           [--capterra-slug <slug>] [--trustpilot-slug <domain>]
Output: JSON to stdout
"""

import argparse
import json
import re
import time

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 12
MAX_REVIEWS_PER_SOURCE = 10
MAX_TEXT_CHARS = 300


def name_to_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def fetch_page(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException:
        pass
    return None


def scrape_g2(slug: str) -> list[dict]:
    url = f"https://www.g2.com/products/{slug}/reviews"
    soup = fetch_page(url)
    if not soup:
        return []

    reviews = []
    # G2 review cards use itemprop="reviewBody" or class patterns
    for item in soup.select("[itemprop='reviewBody'], .review-body, .paper--white p"):
        text = item.get_text(separator=" ").strip()
        if len(text) > 30:
            rating = None
            card = item.find_parent(class_=re.compile(r"review|paper"))
            if card:
                stars = card.find(attrs={"data-rating": True})
                if stars:
                    try:
                        rating = float(stars["data-rating"])
                    except (ValueError, TypeError):
                        pass
            reviews.append({
                "source": "g2",
                "rating": rating,
                "text": text[:MAX_TEXT_CHARS],
            })
        if len(reviews) >= MAX_REVIEWS_PER_SOURCE:
            break
    return reviews


def scrape_capterra(slug: str) -> list[dict]:
    url = f"https://www.capterra.com/p/software/{slug}/"
    soup = fetch_page(url)
    if not soup:
        return []

    reviews = []
    for item in soup.select("[data-testid='review-text'], .review-body__text, p.review"):
        text = item.get_text(separator=" ").strip()
        if len(text) > 30:
            reviews.append({
                "source": "capterra",
                "rating": None,
                "text": text[:MAX_TEXT_CHARS],
            })
        if len(reviews) >= MAX_REVIEWS_PER_SOURCE:
            break
    return reviews


def scrape_trustpilot(domain: str) -> list[dict]:
    url = f"https://www.trustpilot.com/review/{domain}"
    soup = fetch_page(url)
    if not soup:
        return []

    reviews = []
    for item in soup.select("[data-service-review-text-typography], .review-content__text"):
        text = item.get_text(separator=" ").strip()
        if len(text) > 30:
            rating = None
            card = item.find_parent(attrs={"data-service-review-rating": True})
            if card:
                try:
                    rating = float(card["data-service-review-rating"])
                except (ValueError, TypeError):
                    pass
            reviews.append({
                "source": "trustpilot",
                "rating": rating,
                "text": text[:MAX_TEXT_CHARS],
            })
        if len(reviews) >= MAX_REVIEWS_PER_SOURCE:
            break
    return reviews


def main():
    parser = argparse.ArgumentParser(description="Fetch reviews for a company")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--g2-slug", help="G2 slug (default: derived from company name)")
    parser.add_argument("--capterra-slug", help="Capterra slug")
    parser.add_argument("--trustpilot-slug", help="Trustpilot domain (e.g. company.com)")
    args = parser.parse_args()

    default_slug = name_to_slug(args.company)
    g2_slug = args.g2_slug or default_slug
    capterra_slug = args.capterra_slug or default_slug
    trustpilot_slug = args.trustpilot_slug or default_slug

    all_reviews = []
    sources_status = {}

    for label, fn, slug in [
        ("g2", scrape_g2, g2_slug),
        ("capterra", scrape_capterra, capterra_slug),
        ("trustpilot", scrape_trustpilot, trustpilot_slug),
    ]:
        results = fn(slug)
        if results:
            all_reviews.extend(results)
            sources_status[label] = len(results)
        else:
            sources_status[label] = "unavailable"
        time.sleep(1)  # polite delay between sources

    output = {
        "company": args.company,
        "sources_status": sources_status,
        "review_count": len(all_reviews),
        "reviews": all_reviews,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
