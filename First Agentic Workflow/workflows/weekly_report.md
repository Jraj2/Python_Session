# Workflow: Weekly Competitor Report

**Type:** Main orchestration — run every Monday  
**Produces:** Updated Google Sheet + branded HTML report

---

## Objective

Research all tracked competitors, analyze each with Claude, and deliver a branded AIS report to Google Sheets and an HTML file — all in one automated run.

## Pre-Run Checklist

Before starting, verify:

- [ ] `.env` is present and `ANTHROPIC_API_KEY` + `GOOGLE_SHEETS_ID` are filled in
- [ ] `data/competitors.json` exists with at least 1 competitor
- [ ] `data/business_profile.json` exists
- [ ] `credentials/google_service_account.json` is present (for Sheets)
- [ ] `.tmp/` directory is empty (clear it if leftover files from last run)

```bash
# Clear .tmp/ before starting
rm -f ".tmp/"*.json
```

---

## Steps

### Step 1 — Set the run date

```bash
RUN_DATE=$(date +%Y-%m-%d)
mkdir -p "data/runs/$RUN_DATE"
```

On Windows PowerShell:
```powershell
$RUN_DATE = (Get-Date -Format "yyyy-MM-dd")
New-Item -ItemType Directory -Force -Path "data\runs\$RUN_DATE"
```

### Step 2 — Load competitor list

```bash
python -c "import json; comps = json.load(open('data/competitors.json')); print(f'Loaded {len(comps)} competitors')"
```

### Step 3 — Research each competitor

For each competitor in `data/competitors.json`, follow all steps in **`workflows/research_single_competitor.md`**.

**Important:**
- Run competitors **sequentially** (not in parallel) to avoid overwhelming target servers
- Add a **5–10 second sleep** between competitors
- Log each result to `.tmp/run_log.json`

A `run_weekly.py` driver script in the root directory handles this loop programmatically. Example loop logic:

```python
import json, subprocess, time, pathlib, shutil
from datetime import date

run_date = date.today().isoformat()
tmp = pathlib.Path(".tmp")
tmp.mkdir(exist_ok=True)

competitors = json.loads(pathlib.Path("data/competitors.json").read_text())
run_log = []

for comp in competitors:
    name = comp["name"]
    slug = name.lower().replace(" ", "_")
    print(f"\n--- Researching: {name} ---")

    # Steps 1-5: scrape and merge signals
    # (inline the research_single_competitor steps here)
    # ...

    # Step 6: analyze
    signals_path = tmp / f"{slug}_signals.json"
    result = subprocess.run(
        ["python", "tools/analyze_competitor.py", "--competitor-json", str(signals_path)],
        capture_output=True, text=True
    )
    status = "complete" if result.returncode == 0 else "error"
    run_log.append({"competitor": name, "status": status})

    time.sleep(7)  # polite delay

pathlib.Path(".tmp/run_log.json").write_text(json.dumps(run_log, indent=2))
```

### Step 4 — Write to Google Sheets

```bash
python tools/write_to_sheets.py --run-date "$RUN_DATE" --data-dir .tmp/
```

This updates all four tabs with AIS brand formatting and inserts the logo in the Summary tab.

**On failure:** If Google Auth fails, check that the service account email has Editor access to the sheet. Re-run this step alone after fixing — it's safe to re-run.

### Step 5 — Generate HTML report

```bash
python tools/generate_html_report.py --run-date "$RUN_DATE" --data-dir .tmp/
```

Output: `data/runs/<run_date>/competitor_report_<run_date>.html`

Open in Chrome/Edge and use **File → Print → Save as PDF** to produce a PDF version for sharing.

### Step 6 — Archive analysis files

```bash
cp .tmp/*_analysis.json "data/runs/$RUN_DATE/"
```

### Step 7 — Delta check (manual review)

Compare this week's analyses against last week's:

```bash
python -c "
import json, pathlib, glob, os

runs = sorted([d for d in pathlib.Path('data/runs').iterdir() if d.is_dir()])
if len(runs) < 2:
    print('First run — no delta to check')
    exit()

current_dir, prior_dir = runs[-1], runs[-2]
flags = []

for f in current_dir.glob('*_analysis.json'):
    current = json.loads(f.read_text())
    prior_f = prior_dir / f.name
    if not prior_f.exists():
        continue
    prior = json.loads(prior_f.read_text())
    
    threat_delta = int(current.get('threat_level') or 0) - int(prior.get('threat_level') or 0)
    job_delta = int(current.get('active_job_count') or 0) - int(prior.get('active_job_count') or 0)
    
    if threat_delta >= 2:
        flags.append(f'⚠️  {current[\"competitor_name\"]}: threat level rose by {threat_delta}')
    if abs(job_delta) >= 5:
        flags.append(f'📋 {current[\"competitor_name\"]}: job count changed by {job_delta:+d}')

if flags:
    print('FLAGS FOR MANUAL REVIEW:')
    for flag in flags:
        print(' ', flag)
else:
    print('No significant changes flagged.')
"
```

Review any flagged competitors in the HTML report before the week starts.

### Step 8 — Print run summary

```bash
python -c "
import json, pathlib

log = json.loads(pathlib.Path('.tmp/run_log.json').read_text())
complete = sum(1 for r in log if r['status'] == 'complete')
errors   = sum(1 for r in log if r['status'] == 'error')
print(f'Run complete: {complete} succeeded, {errors} errors')
for r in log:
    icon = '✓' if r['status'] == 'complete' else '✗'
    print(f'  {icon} {r[\"competitor\"]}')
"
```

### Step 9 — Clear .tmp/ (optional)

```bash
# Only if CLEAR_TMP=true in .env
rm -f ".tmp/"*.json
```

---

## Scheduling on Windows

1. Create `run_weekly.py` in the `First Agentic Workflow/` root that sequences all steps above
2. Create `run_weekly.bat`:
   ```bat
   @echo off
   cd /d "C:\Users\jayar\copilotxpress_lesson2\First Agentic Workflow"
   python run_weekly.py
   ```
3. Open **Task Scheduler** → Create Basic Task → Weekly → Monday 08:00 AM → Action: run `run_weekly.bat`

---

## Output Files

| File | Description |
|---|---|
| Google Sheet | 4 branded tabs with competitor data, logo in Summary |
| `data/runs/<date>/competitor_report_<date>.html` | Self-contained branded HTML report with AIS logo |
| `data/runs/<date>/*_analysis.json` | Raw Claude analysis, archived for future delta checks |
| `.tmp/run_log.json` | Run status log (cleared next week) |

---

## Improving the Workflow Over Time

When you discover something new (a site blocks your scraper, a competitor's G2 slug changed, a new review platform matters), update this document. That's the WAT self-improvement loop:

1. Identify what broke
2. Fix the tool
3. Verify the fix works
4. Update this workflow with the new approach
