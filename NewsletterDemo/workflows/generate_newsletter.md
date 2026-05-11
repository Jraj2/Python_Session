# Workflow: Generate Newsletter

## Objective
Turn a research JSON file into a fully rendered, email-safe HTML newsletter with optional data charts.

## Tools Used
- `tools/create_infographic.py` — generates Matplotlib chart PNGs
- `tools/upload_image.py` — uploads PNGs to imgBB for email-safe hosting
- `tools/generate_newsletter_html.py` — calls Claude API + Jinja2 + Premailer to produce final HTML

## Inputs
| Input | Description |
|---|---|
| `research_path` | Path to `.tmp/research_{ts}.json` |
| `issue_number` | Current issue number |
| chart specs | Derived from research by inspecting quantitative data |

## Steps

### 1. Identify Chart Opportunities
Read the research JSON sources. Look for numeric data worth visualizing:
- Percentages, rankings, counts → bar or horizontal bar chart
- Data points over time → line chart
- Market share or composition → pie chart

If no numeric data is present in the research, skip to Step 4 (no charts).

### 2. Build Chart Specs
For each chart, create a JSON spec:
```json
{
  "type": "bar",
  "title": "Top AI Frameworks by GitHub Stars (2026)",
  "labels": ["PyTorch", "TensorFlow", "JAX", "MXNet"],
  "values": [82000, 76000, 28000, 10000],
  "ylabel": "GitHub Stars"
}
```

Supported chart types: `bar`, `horizontal_bar`, `line`, `pie`

### 3. Generate Chart PNGs
For each spec:
```
python tools/create_infographic.py --spec '<json_spec>'
```
Note the output path (`.tmp/charts/*.png`).

### 4. Upload Charts to imgBB
For each chart PNG:
```
python tools/upload_image.py --file <chart_png_path>
```
Collect returned URLs. Build manifest:
```json
[
  {"url": "https://i.ibb.co/abc123/chart.png", "caption": "GitHub Stars by Framework (2026)"},
  ...
]
```
Save manifest to `.tmp/chart_manifest_{ts}.json`.

**Fallback if imgBB fails**: Note the failure. Do not include that chart. Proceed without it rather than blocking the whole newsletter.

### 5. Generate HTML Newsletter
```
python tools/generate_newsletter_html.py \
  --research .tmp/research_{ts}.json \
  --charts .tmp/chart_manifest_{ts}.json \
  --issue <issue_number>
```
This calls the Claude API (claude-sonnet-4-6) to write the newsletter copy, then renders it through the Jinja2 template and Premailer CSS inliner.

Output:
- `.tmp/newsletter_{ts}.html` — the final email-ready HTML
- `.tmp/newsletter_{ts}_meta.json` — subject line, story data, read time

## Output Validation
- Open the HTML file and visually check it exists and has content
- Confirm the subject line in the meta JSON looks good
- Pass both paths to `preview_newsletter.py` for human review

## Notes
- The Anthropic API call in Step 5 costs tokens. If the research file is very large, the first 800 chars of each source are used to stay within a reasonable context size.
- Chart captions should be concise (under 10 words) and factual — they appear beneath the chart image in the email.
- The newsletter template (`tools/templates/newsletter.html`) uses table-based layout for Outlook compatibility.
