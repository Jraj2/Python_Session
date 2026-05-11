"""
Fetch and clean text content from a URL.
Usage: python scrape_website.py --url <url>
Output: JSON to stdout
"""

import argparse
import json
import sys

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 10
MAX_CHARS = 12000


def scrape(url: str) -> dict:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"url": url, "error": str(e)}

    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag and meta_tag.get("content"):
        meta_desc = meta_tag["content"].strip()

    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
        tag.decompose()

    body_text = " ".join(soup.get_text(separator=" ").split())
    body_text = body_text[:MAX_CHARS]

    return {
        "url": url,
        "title": title,
        "meta_description": meta_desc,
        "body_text": body_text,
    }


def main():
    parser = argparse.ArgumentParser(description="Scrape clean text from a URL")
    parser.add_argument("--url", required=True, help="URL to scrape")
    args = parser.parse_args()

    result = scrape(args.url)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
