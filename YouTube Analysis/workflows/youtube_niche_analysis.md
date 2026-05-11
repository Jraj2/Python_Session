# YouTube Niche Analysis — Workflow

## Objective
Pull the top AI and AI automation YouTube channels, scrape recent video data, run Claude analysis to surface trending topics and content opportunities, then generate a branded 12-page PDF report.

## Required Inputs
- `YOUTUBE_API_KEY` — YouTube Data API v3 key (Google Cloud Console → Credentials → API key, free)
- `ANTHROPIC_API_KEY` — Anthropic API key (copy from `../First Agentic Workflow/.env`)

## One-time setup

```bash
pip install google-api-python-client reportlab matplotlib anthropic python-dotenv Pillow requests
```

Add both keys to `.env` in this directory:
```
YOUTUBE_API_KEY=<your key>
ANTHROPIC_API_KEY=<your key>
CLAUDE_MODEL=claude-sonnet-4-6
```

---

## Steps

### Step 1 — Discover top AI channels
```bash
python tools/fetch_channels.py
```
Searches YouTube for AI/automation channels across 6 keyword queries. Deduplicates and fetches stats for ~40-60 unique channels.

**Output:** `.tmp/channels.json`
**Quota:** ~650 units (6.5% of 10k daily limit)

---

### Step 2 — Fetch recent video data
```bash
python tools/fetch_videos.py
```
Fetches the 20 most recent videos per channel, including view counts, likes, comments, duration, and tags. Computes `engagement_rate = (likes + comments) / views` per video.

**Output:** `.tmp/videos.json`
**Quota:** ~600 units

---

### Step 3 — Claude trend analysis
```bash
python tools/analyze_trends.py
```
Sends channel and video summaries to Claude (claude-sonnet-4-6) with a structured prompt. Claude clusters videos into AI sub-topics, identifies high-performing title patterns, finds content gaps, and generates 5 content strategy recommendations.

**Output:** `.tmp/analysis.json`
**Quota:** No YouTube units. Uses ~$0.02-0.04 in Anthropic API credits.

---

### Step 4 — Generate charts
```bash
python tools/generate_charts.py
```
Creates 7 Matplotlib charts with the AIS dark brand theme (#1A1E22 background, #00C9A0 accent):
1. Top channels by subscriber count
2. Top channels by engagement rate
3. Top 10 most-viewed videos
4. Topic distribution pie chart
5. Video length vs. views scatter
6. Upload frequency (last 12 weeks)
7. Engagement rate by topic cluster

**Output:** `.tmp/charts/*.png` (7 files)
**Quota:** None — fully local.

---

### Step 5 — Build the PDF report
```bash
python tools/generate_pdf.py
```
Assembles a branded 12-page PDF (AIS logo on cover, branded footer on every page):
| # | Page |
|---|------|
| 1 | Cover (AIS logo + report title) |
| 2 | Executive Summary + stat cards |
| 3 | Top Channels — Subscriber Count |
| 4 | Top Channels — Engagement Rate |
| 5 | Top Performing Videos |
| 6 | Content Topic Landscape |
| 7 | Engagement Rate by Topic |
| 8 | Video Length vs. Views |
| 9 | Upload Velocity (12-week trend) |
| 10 | Title Patterns & Trending Keywords |
| 11 | Content Gaps & Opportunities |
| 12 | Strategy Recommendations |

**Output:** `.tmp/youtube_analysis_YYYY-MM-DD.pdf`
**Quota:** None — fully local.
**Note:** AIS logo loaded from `assets/AIS_logo.png`. Run Steps 1–4 first to populate `.tmp/`.

---

## Expected outputs

| File | Description |
|------|-------------|
| `.tmp/channels.json` | ~50 channel records with subscriber/view stats |
| `.tmp/videos.json` | ~800 video records with engagement metrics |
| `.tmp/analysis.json` | Claude analysis: topics, gaps, title patterns, recommendations |
| `.tmp/charts/*.png` | 7 branded Matplotlib charts |
| `.tmp/youtube_analysis_YYYY-MM-DD.pdf` | Final 12-page branded PDF report |

---

---

## Running on Modal (automated weekly)

The pipeline is deployed to Modal and runs every **Monday at 08:00 IST** (02:30 UTC) without any local machine required.

### One-time setup

```powershell
# 1. Create the Modal secret (paste values from your .env)
modal secret create yt-analysis-secrets `
  YOUTUBE_API_KEY=<your key> `
  ANTHROPIC_API_KEY=<your key> `
  CLAUDE_MODEL=claude-sonnet-4-6

# 2. Deploy and register the weekly cron
cd "c:\Users\jayar\copilotxpress_lesson2\YouTube Analysis"
modal deploy modal_app.py
```

### Manual test run

```powershell
modal run modal_app.py
```

Runs the full 5-step pipeline immediately (takes ~10–15 min). Logs stream to your terminal.

### Download the PDF

```powershell
modal volume get yt-analysis-outputs youtube_analysis_YYYY-MM-DD.pdf
```

Replace `YYYY-MM-DD` with today's date (e.g. `youtube_analysis_2026-05-04.pdf`).

### Redeploy after code changes

```powershell
modal deploy modal_app.py
```

Modal re-uploads the source files and updates the cron. No restart needed.

---

## Edge cases & notes

**Quota budget:** Total ~1,250 units per full run (12.5% of the 10k daily free limit). Safe to re-run daily.

**Hidden subscriber counts:** Channels that hide their subscriber count return 0. They're included in the dataset but ranked last in subscriber charts.

**Rate limiting (HttpError 429):** If you hit a quota error mid-run, wait 60 seconds and re-run from the failed step. Each tool writes its output independently — you don't need to restart from Step 1.

**YouTube Shorts:** Videos under 60 seconds are included in the dataset. Claude's analysis accounts for this — Shorts tend to have inflated engagement rates and different viewer behavior.

**Anthropic API cost:** `analyze_trends.py` sends ~3,000–5,000 input tokens and receives ~4,000 output tokens. Estimated cost per run: $0.02–$0.04.

**Archiving runs:** To archive a run before re-running, copy `.tmp/` to `data/runs/YYYY-MM-DD/`.

**Updating seed keywords:** Edit the `SEED_KEYWORDS` list in `tools/fetch_channels.py` to pivot to a different sub-niche (e.g. "n8n automation", "AI agents", "Claude tutorials").
