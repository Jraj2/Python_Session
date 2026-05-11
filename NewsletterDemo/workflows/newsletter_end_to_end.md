# Workflow: Newsletter End-to-End

## Objective
Produce and deliver a complete newsletter issue on a given topic, from research through email delivery.

## Trigger
User says something like: "make a newsletter about X", "write this week's newsletter on Y", "create issue N about Z".

## Required Inputs
- `topic` — the subject of the newsletter (e.g. "AI trends this week")
- `issue_number` — the issue number (ask the user if not provided; default 1)
- `days_back` — how many days of recency to search (default: 7)

## Step-by-Step Execution

### Step 1 — Duplicate Check
Read: `workflows/research_topic.md`

Run:
```
python tools/check_duplicates.py --research <most_recent_research_file>
```
If no prior research exists, skip this step.

If the duplicate check fails (exit code 1), inform the user and suggest a more specific angle or different time window. Do not proceed without user confirmation or `--force`.

### Step 2 — Research
Read: `workflows/research_topic.md`

Run:
```
python tools/research_topic.py --topic "<topic>" --days <days_back> --results 8
```
Note the output path (e.g. `.tmp/research_20260422_143000.json`).

Validate: at least 3 sources were returned. If fewer, broaden the topic or increase `--days`.

### Step 3 — Identify Chart Opportunities
Read the research JSON. Look for:
- Quantitative comparisons (rankings, percentages, counts)
- Trends over time (time-series data)
- Proportions or market share (pie/donut data)
- Before/after metrics

For each chart opportunity (aim for 2-3 per issue), define a spec:
```json
{"type": "bar", "title": "...", "labels": [...], "values": [...], "ylabel": "..."}
```

If the research has no clear quantitative data, skip charts and proceed with no chart manifest.

### Step 4 — Generate Charts
Read: `workflows/generate_newsletter.md`

For each chart spec, run:
```
python tools/create_infographic.py --spec '<json_spec>'
```
Note each output PNG path.

### Step 5 — Upload Charts
For each chart PNG, run:
```
python tools/upload_image.py --file <chart_path>
```
Collect all returned URLs. Build a chart manifest JSON:
```json
[{"url": "https://...", "caption": "Caption text"}, ...]
```
Save to `.tmp/chart_manifest_{timestamp}.json`.

If imgBB upload fails: fall back to base64 inline (omit the chart from the manifest and let the generator embed it). Log the failure.

### Step 6 — Generate Newsletter HTML
Run:
```
python tools/generate_newsletter_html.py \
  --research <research_path> \
  --charts <manifest_path> \
  --issue <issue_number>
```
Note the output HTML path.

### Step 7 — Preview (Human Approval Gate)
Read: `workflows/review_and_send.md`

Run:
```
python tools/preview_newsletter.py --file <html_path>
```

**STOP. Do not proceed.** Ask the user:
> "The newsletter is open in your browser. Does it look good? Say 'approve and send' to deliver, describe any changes you'd like, or say 'cancel' to abort."

If the user requests changes: go back to Step 6 (with revised instructions) or Step 2 (for research changes).

### Step 8 — Send
Only after explicit user approval. Read: `workflows/review_and_send.md`

Get the subject line from the newsletter metadata file (`.tmp/newsletter_*_meta.json`), or ask the user to confirm it.

Run dry-run first:
```
python tools/send_newsletter.py --file <html_path> --subject "<subject>" --dry-run
```
Show the user the recipient count. Ask for final confirmation before the live send.

Run live send:
```
python tools/send_newsletter.py --file <html_path> --subject "<subject>"
```

### Step 9 — Archive
Record the research sources to prevent future duplication:
```
python tools/check_duplicates.py --research <research_path> --record
```

Report to the user: how many emails sent, any failures, and where the send log is.

## Edge Cases
- **Tavily returns 0 results**: API key may be invalid or quota exhausted. Check `.env` and Tavily dashboard.
- **imgBB quota exceeded**: Fall back to base64 images for this issue. Note in the send log.
- **SendGrid auth failure**: Verify `SENDGRID_API_KEY` and that the sender email has passed Single Sender Verification in the SendGrid console.
- **No active subscribers**: Remind user to add subscribers with `python tools/manage_subscribers.py add --email X --name Y`.
