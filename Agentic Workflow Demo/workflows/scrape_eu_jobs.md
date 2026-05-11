# Workflow: Scrape Europe Sales + Project Manager Jobs → Excel

## Objective
Collect up to 500 remote job listings in the **Sales** and **Project Manager** categories that are specifically open to European candidates, and export to a formatted Excel file.

---

## Required Inputs

| Input | Source |
|-------|--------|
| `FIRECRAWL_API_KEY` | `.env` file |
| Sales jobs page | `https://dailyremote.com/remote-sales-jobs` |
| Project Manager jobs page | `https://dailyremote.com/remote-project-manager-jobs` |

---

## Tools Used

| Step | Script | Purpose |
|------|--------|---------|
| 1 | `tools/scrape_eu_category_jobs.py` | Scrapes both category pages, filters for European locations, saves `.tmp/eu_jobs_raw.json` |
| 2 | `tools/export_to_excel.py` | Reads JSON, exports formatted `.tmp/eu_jobs_<YYYYMMDD>.xlsx` |

---

## Steps

```bash
# Step 1: Scrape EU-filtered jobs (target 500, cap at 250 pages)
python tools/scrape_eu_category_jobs.py

# Custom target / page cap:
python tools/scrape_eu_category_jobs.py --target 500 --max-pages 250

# Step 2: Export to Excel
python tools/export_to_excel.py --input .tmp/eu_jobs_raw.json --output .tmp/eu_jobs_20260427.xlsx
```

---

## Expected Output

- `.tmp/eu_jobs_raw.json` — raw EU-filtered job objects (intermediate; regeneratable)
- `.tmp/eu_jobs_<YYYYMMDD>.xlsx` — final deliverable with 10 columns:

| Column | Description |
|--------|-------------|
| Job Title | Role name |
| Company | Employer (visible on featured listings only) |
| Location / Timezone | European country or region |
| Job Type | Full-time / Part-time / Contract / Freelance |
| Category | Department (Sales, Software Development, etc.) |
| Source Category | Which category page the job came from (Sales or Project Manager) |
| Salary | Compensation if listed |
| Experience Required | e.g. "2-5 yrs exp" |
| Date Posted | When posted |
| Listing URL | Clickable link to full job post |

---

## Location Filter Logic

Jobs are included when their location tag contains any of these keywords (case-insensitive substring match):

- **Regions**: Europe, European, EMEA, EU
- **British Isles**: UK, United Kingdom, England, Scotland, Wales, Ireland
- **Western Europe**: Germany, France, Spain, Italy, Portugal, Netherlands, Belgium, Austria, Switzerland, Luxembourg, etc.
- **Nordics**: Sweden, Norway, Denmark, Finland, Iceland
- **Eastern/Central**: Poland, Czech, Romania, Hungary, Bulgaria, Croatia, Serbia, etc.
- **Southern**: Greece, Cyprus, Malta

Excludes: Worldwide, United States, Canada, APAC, Latin America, etc.

---

## Scraping Strategy

- Pages are fetched in **round-robin** across both categories (one PM page, one Sales page, repeat)
- Scraper stops when **target EU jobs** are collected OR **max-pages** cap is hit
- 0.8s delay between requests to avoid rate-limiting
- Deduplication by URL across all pages

---

## Edge Cases & Known Issues

- **EU job density**: ~5-8% of Sales listings and ~10-20% of PM listings are EU-specific. Expect to scrape ~150-200 total pages to collect 500 EU jobs.
- **Firecrawl credits**: Each page scrape = 1 credit. 250 pages = 250 credits. Check balance with `app.get_credit_usage()` before large runs.
- **Company name**: Most listings don't display company name in card view — this is a site limitation (premium feature).
- **Location filter is post-scrape**: The site doesn't support server-side location filtering via URL params — all filtering happens in the script.

---

## Notes

- The scraper alternates between PM and Sales pages for balanced category representation.
- Pagination URL pattern: `{base_url}/?page=N` (query parameter, not path-based).
- Last validated: 2026-04-27
