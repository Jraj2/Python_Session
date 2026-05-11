"""
Scrape job postings from a company's careers page.
Usage: python fetch_jobs.py --careers-url <url>
Output: JSON to stdout
"""

import argparse
import json
import re

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
MAX_JOBS = 50

# Known job board embed patterns → their direct API/list URL transforms
JOB_BOARD_PATTERNS = {
    "lever.co": lambda url: url,  # Lever pages are directly scrapable
    "boards.greenhouse.io": lambda url: url,
    "apply.workable.com": lambda url: url,
    "jobs.ashbyhq.com": lambda url: url,
}

# Common heading levels and classes that contain job titles
JOB_TITLE_SELECTORS = [
    "h1", "h2", "h3", "h4",
    "[class*='job-title']",
    "[class*='position-title']",
    "[class*='role-title']",
    "[class*='opening']",
    "[class*='listing']",
    "li[class*='job']",
    "div[class*='job'] h3",
    "div[class*='role'] h3",
]

# Departments / team labels often appear near job titles
DEPARTMENT_SELECTORS = [
    "[class*='department']",
    "[class*='team']",
    "[class*='category']",
]

# Words that indicate these are real job titles rather than nav links
JOB_KEYWORDS = re.compile(
    r"\b(engineer|manager|director|analyst|designer|scientist|"
    r"developer|lead|head|vp|president|specialist|coordinator|"
    r"associate|executive|recruiter|sales|marketing|product|"
    r"operations|finance|legal|support|success|growth|data|"
    r"security|devops|cloud|mobile|backend|frontend|fullstack|"
    r"research|content|brand|account)\b",
    re.IGNORECASE,
)


def detect_job_board_redirect(soup: BeautifulSoup, base_url: str) -> str | None:
    """Check if the page is just a redirect to a hosted job board."""
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        for board in JOB_BOARD_PATTERNS:
            if board in href:
                return href
    # Also check iframes
    for iframe in soup.find_all("iframe", src=True):
        src = iframe["src"]
        for board in JOB_BOARD_PATTERNS:
            if board in src:
                return src
    return None


def extract_jobs(soup: BeautifulSoup) -> list[dict]:
    jobs = []
    seen = set()

    for selector in JOB_TITLE_SELECTORS:
        for el in soup.select(selector):
            text = el.get_text(separator=" ").strip()
            # Filter: must look like a job title, not too long, not already seen
            if (
                text
                and len(text) < 120
                and text not in seen
                and JOB_KEYWORDS.search(text)
            ):
                department = ""
                # Look for a nearby department label (sibling or parent child)
                parent = el.find_parent()
                if parent:
                    for dept_sel in DEPARTMENT_SELECTORS:
                        dept_el = parent.select_one(dept_sel)
                        if dept_el:
                            department = dept_el.get_text(separator=" ").strip()
                            break

                seen.add(text)
                jobs.append({"title": text, "department": department})

            if len(jobs) >= MAX_JOBS:
                return jobs

    return jobs


def fetch_and_parse(url: str) -> tuple[list[dict], str]:
    """Fetch a URL, follow one job-board redirect if present, extract jobs."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        return [], str(e)

    soup = BeautifulSoup(resp.text, "html.parser")

    # Try one level of redirect to a known job board
    redirect = detect_job_board_redirect(soup, url)
    if redirect and redirect != url:
        try:
            resp2 = requests.get(redirect, headers=HEADERS, timeout=TIMEOUT)
            resp2.raise_for_status()
            soup = BeautifulSoup(resp2.text, "html.parser")
        except requests.RequestException:
            pass  # Fall back to original page

    return extract_jobs(soup), ""


def main():
    parser = argparse.ArgumentParser(description="Fetch job postings from a careers page")
    parser.add_argument("--careers-url", required=True, help="URL of the company's careers/jobs page")
    args = parser.parse_args()

    jobs, error = fetch_and_parse(args.careers_url)

    output = {
        "careers_url": args.careers_url,
        "job_count": len(jobs),
        "jobs": jobs,
    }
    if error:
        output["error"] = error

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
