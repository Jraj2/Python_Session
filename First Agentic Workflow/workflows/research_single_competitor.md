# Workflow: Research Single Competitor

**Type:** Per-competitor research  
**Called by:** `weekly_report.md` in a loop, or run manually for a single competitor test.

---

## Objective

Collect all four signal types for one competitor (website, pricing, reviews, jobs), merge them into a signals file, and run Claude analysis to produce a structured analysis JSON.

## Required Inputs

- Competitor entry from `data/competitors.json`:
  - `name` (required)
  - `website_url` (required)
  - `careers_url` (required — verify it loads in a browser if you get 0 jobs)
  - `g2_slug`, `capterra_slug`, `trustpilot_slug` (optional but improve review quality)

---

## Steps

All commands assume you are in the `First Agentic Workflow/` directory. Replace `<name>`, `<url>`, etc. with the competitor's actual values. Use a safe filename version of the name (lowercase, underscores) for file output.

```bash
COMPETITOR="Crayon"
SLUG="crayon"
WEBSITE="https://www.crayon.co"
CAREERS="https://www.crayon.co/careers"
```

### Step 1 — Scrape homepage

```bash
python tools/scrape_website.py --url "$WEBSITE" > ".tmp/${SLUG}_website.json"
```

**On failure (error in JSON output):** Log the error, leave the file with `{ "error": "..." }`, continue. Claude will note the data gap.

### Step 2 — Scrape pricing page

```bash
python tools/scrape_website.py --url "${WEBSITE}/pricing" > ".tmp/${SLUG}_pricing.json"
```

If that returns empty body text, try `/plans`:
```bash
python tools/scrape_website.py --url "${WEBSITE}/plans" > ".tmp/${SLUG}_pricing.json"
```

**On failure:** Same as Step 1 — log and continue.

### Step 3 — Fetch customer reviews

```bash
python tools/fetch_reviews.py \
  --company "$COMPETITOR" \
  --g2-slug "$SLUG" \
  --capterra-slug "$SLUG" \
  --trustpilot-slug "${WEBSITE#https://}" \
  > ".tmp/${SLUG}_reviews.json"
```

Review sites frequently block scrapers. If all three sources return `"unavailable"`, that's expected — Claude will analyze from other signals. Do **not** retry aggressively (no more than once per source per run).

### Step 4 — Fetch job postings

```bash
python tools/fetch_jobs.py --careers-url "$CAREERS" > ".tmp/${SLUG}_jobs.json"
```

**On failure:** If the careers page returns 0 jobs, check if they use Lever/Greenhouse (the tool handles one level of redirect automatically). If still 0, the company may have no open roles — that's valid data.

### Step 5 — Merge signals

Create `.tmp/<slug>_signals.json` by combining the four files:

```python
# merge_signals.py helper — or do this inline in run_weekly.py
import json, pathlib

slug = "crayon"
tmp = pathlib.Path(".tmp")

signals = {
    "competitor_name": "Crayon",
    "website_url": "https://www.crayon.co",
    "run_date": "2026-04-28",
    "website": json.loads((tmp / f"{slug}_website.json").read_text()),
    "pricing": json.loads((tmp / f"{slug}_pricing.json").read_text()),
    "reviews": json.loads((tmp / f"{slug}_reviews.json").read_text()),
    "jobs":    json.loads((tmp / f"{slug}_jobs.json").read_text()),
}

(tmp / f"{slug}_signals.json").write_text(json.dumps(signals, indent=2))
```

### Step 6 — Analyze with Claude

```bash
python tools/analyze_competitor.py --competitor-json ".tmp/${SLUG}_signals.json"
```

This writes `.tmp/<slug>_analysis.json`. Claude's response will include all 15 structured fields plus `opportunities_for_ais`.

**On failure:**
- If Claude returns malformed JSON: the tool retries once automatically
- If retry also fails: a placeholder with `parse_error` is written — skip this competitor in the Sheets/HTML output

### Step 7 — Log status

Append to `.tmp/run_log.json`:

```json
{"competitor": "Crayon", "status": "complete", "signals_available": ["website", "pricing", "reviews"]}
```

---

## Failure Rules

| Situation | Action |
|---|---|
| 1–2 signals unavailable | Run analysis on remaining signals; Claude notes gaps |
| 3–4 signals unavailable | Still run analysis; Claude will flag "Insufficient data" across fields |
| `analyze_competitor.py` API error | Retry once after 30s; if fails again, write placeholder and move on |
| Claude returns malformed JSON | Tool retries once automatically with stronger formatting instruction |
| Careers page returns 0 jobs | Valid data — record as `active_job_count: 0` |

**A single competitor failure never halts the full weekly run.**

---

## Output

On success: `.tmp/<slug>_analysis.json` with all structured fields.  
The weekly_report.md orchestrator reads this file for both Sheets and HTML output.
