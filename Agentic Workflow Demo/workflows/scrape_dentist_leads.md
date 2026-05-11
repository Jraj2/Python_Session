# Workflow: Scrape US Dentist Lead List → Excel

## Objective
Build a targeted lead list of US dental practices across the 10 most populous states, pulling contact info from YellowPages.com and exporting to a formatted Excel file.

---

## Required Inputs

| Input | Source |
|-------|--------|
| `FIRECRAWL_API_KEY` | `.env` file |
| Target directory | YellowPages.com dentist search |
| States | CA, TX, FL, NY, PA, IL, OH, GA, NC, MI |

---

## Tools Used

| Step | Script | Purpose |
|------|--------|---------|
| 1 | `tools/scrape_dentist_leads.py` | Scrapes YP by state, extracts lead fields, saves `.tmp/dentist_leads_raw.json` |
| 2 | `tools/export_to_excel.py` | Reads JSON, auto-detects `dentist_leads` schema, exports `.tmp/dentist_leads_<YYYYMMDD>.xlsx` |

---

## Steps

```bash
# Step 1: Scrape dentist leads (default: 1,000 target, 4 pages/state)
python tools/scrape_dentist_leads.py

# Custom scale:
python tools/scrape_dentist_leads.py --target 500 --pages-per-state 2

# Step 2: Export to Excel (auto-detects dentist_leads preset)
python tools/export_to_excel.py --input .tmp/dentist_leads_raw.json
```

---

## Expected Output

- `.tmp/dentist_leads_raw.json` — raw lead objects (intermediate; regeneratable)
- `.tmp/dentist_leads_<YYYYMMDD>.xlsx` — final deliverable with 11 columns:

| Column | Description |
|--------|-------------|
| Practice Name | Name of the dental practice |
| Phone Number | Direct office phone (primary outreach field) |
| Street Address | Street address |
| City | City |
| State | 2-letter state code |
| ZIP Code | Postal code |
| Specialties | Categories from YP (e.g. "Dentists, Cosmetic Dentistry") |
| Website | Practice website URL (clickable) |
| Rating | Star rating (1.0–5.0) |
| Review Count | Number of reviews |
| YellowPages URL | Link to full YP listing (clickable) |

---

## Source & Scale

- **Source**: YellowPages.com (`/search?search_terms=dentist&geo_location_terms={State}`)
- **Pagination**: `&page=N` (query parameter)
- **Per page**: ~30 listings
- **Target**: 1,000 leads = ~4 pages × 10 states = 40 Firecrawl credits
- **Deduplication**: by phone number (normalized digits only)

---

## States Covered (Top 10 by Population)

| State | Abbr |
|-------|------|
| California | CA |
| Texas | TX |
| Florida | FL |
| New York | NY |
| Pennsylvania | PA |
| Illinois | IL |
| Ohio | OH |
| Georgia | GA |
| North Carolina | NC |
| Michigan | MI |

---

## Edge Cases & Known Issues

- **Chain practices** (e.g. Aspen Dental): May appear across multiple states. Deduplication by phone handles national toll-free numbers partially, but local branch phones will appear once each.
- **No address listings**: Some results have "Serving the CA Area" instead of a street address — these are still included if they have a phone.
- **YP rate limiting**: 1.2s delay between page requests is built in. Increase if errors appear.
- **Firecrawl credits**: ~40 credits for default 1,000-lead run. Check with `app.get_credit_usage()` before running.

---

## Notes

- The `export_to_excel.py` tool auto-detects the `dentist_leads` schema from the filename — no `--preset` flag needed.
- Header row is styled green (#1F6B3A) to visually distinguish lead sheets from job sheets.
- Last validated: 2026-04-27
