# Workflow: Setup Business Profile

**Type:** One-time setup  
**Run once before your first weekly report.**

---

## Objective

Establish AIS's identity in the system, discover an initial competitor list, and verify the full pipeline works end-to-end before automating the weekly run.

## Required Inputs

- Anthropic API key
- Basic description of your product (even rough notes are fine)
- Google Cloud service account credentials (for Sheets output)
- A Google Sheet to write into (or permission to create one)

---

## Steps

### Step 1 — Add API credentials to `.env`

Open `.env` and fill in:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
CLAUDE_MODEL=claude-sonnet-4-6
GOOGLE_SHEETS_ID=<ID from your Google Sheet URL>
GOOGLE_CREDENTIALS_JSON=./credentials/google_service_account.json
```

Test the Anthropic key:
```bash
python -c "import anthropic, os; from dotenv import load_dotenv; load_dotenv(); c = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY']); r = c.messages.create(model='claude-sonnet-4-6', max_tokens=10, messages=[{'role':'user','content':'hi'}]); print('OK:', r.content[0].text)"
```

### Step 2 — Set up Google Sheets access

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → enable **Google Sheets API** and **Google Drive API**
3. Create a Service Account → download the JSON key → save to `credentials/google_service_account.json`
4. Open your Google Sheet → Share → paste the service account email → set role to **Editor**
5. Copy the Sheet ID from the URL: `docs.google.com/spreadsheets/d/<SHEET_ID>/edit`
6. Paste into `GOOGLE_SHEETS_ID` in `.env`

### Step 3 — Create your business profile

Create `data/business_profile.json` with your product information:

```json
{
  "product_name": "AIS",
  "product_description": "A SaaS platform that helps businesses research competitors and track market changes automatically.",
  "target_customer": "Early-stage SaaS founders and product teams who need competitive intelligence without a dedicated analyst",
  "primary_value_prop": "Automated weekly competitor research powered by AI — no manual Googling required",
  "pricing_model": "freemium",
  "geography": "Global, English-language markets",
  "stage": "pre-launch",
  "key_differentiators": [
    "AI-powered analysis using Claude",
    "Automated weekly cadence",
    "Branded reports in Google Sheets and HTML",
    "No search API required to get started"
  ]
}
```

Fill in your actual details. Be specific — Claude uses this to understand what makes a company a competitor vs. an adjacent player.

### Step 4 — Discover competitors

```bash
cd "First Agentic Workflow"
python tools/discover_competitors.py --profile-json data/business_profile.json
```

Claude will suggest 8–12 competitors. Review each one:
- Press **Enter** to accept all
- Type `remove 2,5` to remove by number
- Type `add` to manually add a competitor

This writes `data/competitors.json`.

### Step 5 — Verify and enrich the competitor list

Open `data/competitors.json`. For each competitor:

1. Check that `careers_url` actually leads to their jobs page (quick browser check)
2. Verify the G2 slug by visiting: `https://www.g2.com/products/<g2_slug>/reviews`
3. Verify the Capterra slug: `https://www.capterra.com/p/software/<capterra_slug>/`
4. Verify Trustpilot: `https://www.trustpilot.com/review/<trustpilot_slug>`

Update any incorrect slugs directly in the JSON file. These are best-effort scraping targets — if a company isn't on G2/Capterra, that's fine; the review tool will mark it as unavailable and Claude will note the data gap.

### Step 6 — Run an end-to-end test

Pick one competitor from your list and run the full research pipeline manually. Follow **`workflows/research_single_competitor.md`** for that one competitor, then run both output tools:

```bash
python tools/write_to_sheets.py --run-date 2026-04-23 --data-dir .tmp/
python tools/generate_html_report.py --run-date 2026-04-23 --data-dir .tmp/
```

### Step 7 — Verify outputs

- **Google Sheet:** Open it and confirm the "Weekly Snapshot", "History", and "Summary" tabs are formatted with AIS brand colors (dark teal headers, white text)
- **HTML report:** Open `data/runs/2026-04-23/competitor_report_2026-04-23.html` in a browser. Confirm:
  - AIS logo appears in the header
  - Dark background, teal accent, threat level badges are color-coded
  - Competitor cards show all available signals

### Step 8 — Schedule the weekly run

Once the test passes, set up Task Scheduler (Windows) to run `weekly_report.md` every Monday morning. Create a `run_weekly.py` driver script in the root that sequences all the weekly steps programmatically, then point Task Scheduler at it.

---

## Exit Condition

Setup is complete when:
- [x] `.env` has valid Anthropic + Google credentials
- [x] `data/business_profile.json` exists with real content
- [x] `data/competitors.json` has ≥3 confirmed competitors with verified URLs
- [x] One end-to-end test run completed without errors
- [x] Google Sheet is visible and branded correctly
- [x] HTML report renders with AIS logo and correct brand colors
