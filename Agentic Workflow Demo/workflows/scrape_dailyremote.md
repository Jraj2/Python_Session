# Workflow: Scrape DailyRemote Job Listings → Excel

## Objective
Scrape the first ~200 remote job listings from dailyremote.com and export them to a formatted Excel file for manual review and filtering.

---

## Required Inputs

| Input | Source |
|-------|--------|
| `FIRECRAWL_API_KEY` | `.env` file |
| Target site | `https://dailyremote.com/` |
| Page range | Pages 1–10 (≈20 jobs/page) |

---

## Tools Used

| Step | Script | Purpose |
|------|--------|---------|
| 1 | `tools/scrape_job_listings.py` | Scrapes paginated pages via Firecrawl, writes `.tmp/jobs_raw.json` |
| 2 | `tools/export_to_excel.py` | Reads JSON, exports formatted `.tmp/dailyremote_jobs_<YYYYMMDD>.xlsx` |

---

## Steps

```bash
# Step 1: Scrape job listings (10 pages ≈ 200 jobs)
python tools/scrape_job_listings.py

# Optional: scrape fewer pages for a quick test
python tools/scrape_job_listings.py --pages 2

# Step 2: Export to Excel
python tools/export_to_excel.py
```

---

## Expected Output

- `.tmp/jobs_raw.json` — raw array of job objects (intermediate; regeneratable)
- `.tmp/dailyremote_jobs_<YYYYMMDD>.xlsx` — final deliverable with:
  - 8 columns: Job Title, Company, Location / Timezone, Job Type, Category, Salary, Date Posted, Listing URL
  - Frozen header row with blue styling
  - Auto-sized columns
  - Clickable hyperlinks in the URL column

---

## Fields Captured Per Job

| Column | Description |
|--------|-------------|
| Job Title | Role name |
| Company | Employer name |
| Location / Timezone | Remote restriction (e.g. "Worldwide", "US only", "EST") |
| Job Type | Full-time / Part-time / Contract / Freelance |
| Category | Department (Engineering, Design, Marketing, etc.) |
| Salary | Compensation range if listed; "N/A" if absent |
| Date Posted | Date or relative time (e.g. "2 days ago") |
| Listing URL | Clickable link to the full job post |

---

## Pagination URL Pattern

- Page 1: `https://dailyremote.com/remote-jobs/`
- Pages 2–N: `https://dailyremote.com/remote-jobs/?page={N}`

The site uses query-parameter pagination (not path-based). The scraper stops early if a page returns zero job cards.

---

## Edge Cases & Known Issues

- **Rate limiting**: A 1.5s delay is built in between page requests. If Firecrawl returns rate-limit errors, increase the `time.sleep()` value in `scrape_job_listings.py`.
- **Pagination URL format**: If page 2+ returns 0 jobs, the URL pattern may have changed. Check the site manually and update `page_url()` in the script.
- **Firecrawl credits**: Each page scrape consumes Firecrawl API credits. 10 pages ≈ 10 credits.
- **Empty salary field**: Many listings don't show salary. These are populated with "N/A" in the Excel output.
- **Duplicate detection**: The scraper deduplicates by URL across pages to prevent double-counting promoted listings.

---

## Notes

- Extraction uses Firecrawl's LLM-powered `extract` mode with a strict JSON schema — no CSS selectors to maintain.
- The intermediate `.tmp/jobs_raw.json` file is disposable; re-run `scrape_job_listings.py` to regenerate it.
- To change the number of pages scraped, use `--pages N` flag on the scraper.
- Last validated: 2026-04-27
