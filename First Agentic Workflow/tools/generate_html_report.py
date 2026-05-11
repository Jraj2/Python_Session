"""
Generate a branded AIS HTML competitor intelligence report.
Usage: python generate_html_report.py --run-date YYYY-MM-DD --data-dir .tmp/
Output: data/runs/<run-date>/competitor_report_<run-date>.html
"""

import argparse
import base64
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"


def load_brand() -> dict:
    brand_path = ASSETS_DIR / "brand_config.json"
    if brand_path.exists():
        with open(brand_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "colors": {
            "bg_primary": "#1A1E22",
            "bg_surface": "#0D2626",
            "accent": "#00C9A0",
            "text_primary": "#FFFFFF",
            "text_muted": "#A0B0B0",
            "danger": "#E05555",
            "warning": "#F0A030",
        },
        "report_footer": "Confidential — AIS Internal Use Only",
    }


def logo_as_base64() -> str:
    logo_path = ASSETS_DIR / "AIS_logo.png"
    if not logo_path.exists():
        return ""
    with open(logo_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def load_analyses(data_dir: str) -> list[dict]:
    analyses = []
    for path in Path(data_dir).glob("*_analysis.json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "parse_error" not in data:
                analyses.append(data)
    return sorted(analyses, key=lambda a: -(int(a.get("threat_level") or 0)))


def load_profile() -> dict:
    path = DATA_DIR / "business_profile.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def threat_color(level, brand: dict) -> str:
    try:
        level = int(level)
    except (TypeError, ValueError):
        return brand["colors"]["text_muted"]
    if level >= 4:
        return brand["colors"]["danger"]
    if level <= 2:
        return brand["colors"]["accent"]
    return brand["colors"]["warning"]


def threat_label(level) -> str:
    mapping = {1: "Minimal", 2: "Low", 3: "Moderate", 4: "High", 5: "Critical"}
    try:
        return mapping.get(int(level), "Unknown")
    except (TypeError, ValueError):
        return "Unknown"


def render_competitor_card(a: dict, brand: dict) -> str:
    c = brand["colors"]
    t_color = threat_color(a.get("threat_level"), brand)
    t_label = threat_label(a.get("threat_level"))
    hiring = ", ".join(a.get("key_hiring_areas") or []) or "—"
    signals = ", ".join(a.get("signals_available") or []) or "—"
    opps = a.get("opportunities_for_ais", "")
    changes = a.get("notable_changes", "—")

    return f"""
    <div class="competitor-card">
      <div class="card-header">
        <div>
          <div class="competitor-name">{a.get('competitor_name', 'Unknown')}</div>
          <div class="competitor-url"><a href="{a.get('website_url', '#')}" target="_blank">{a.get('website_url', '')}</a></div>
        </div>
        <div class="threat-badge" style="background:{t_color}">
          {t_label} Threat &nbsp; {a.get('threat_level', '?')}/5
        </div>
      </div>

      <div class="card-grid">
        <div class="signal-block">
          <div class="signal-label">Messaging</div>
          <div>{a.get('messaging_summary', '—')}</div>
        </div>
        <div class="signal-block">
          <div class="signal-label">Pricing</div>
          <div><strong>{a.get('pricing_tier', '—')}</strong></div>
          <div class="muted">{a.get('pricing_notes', '')}</div>
        </div>
        <div class="signal-block">
          <div class="signal-label">Reviews</div>
          <div>{a.get('review_sentiment', '—')}
            {'&nbsp;&nbsp;⭐ ' + str(a.get('avg_rating')) if a.get('avg_rating') else ''}
          </div>
          <div class="muted">{a.get('top_review_theme', '')}</div>
        </div>
        <div class="signal-block">
          <div class="signal-label">Hiring</div>
          <div><strong>{a.get('active_job_count', 0)}</strong> open roles</div>
          <div class="muted">{hiring}</div>
        </div>
      </div>

      <div class="signal-block" style="margin-top:12px">
        <div class="signal-label">Threat Rationale</div>
        <div>{a.get('threat_rationale', '—')}</div>
      </div>

      <div class="signal-block" style="margin-top:12px">
        <div class="signal-label">Notable Changes This Week</div>
        <div>{changes}</div>
      </div>

      {'<div class="opp-block"><div class="signal-label" style="color:#00C9A0">Opportunities for AIS</div><div>' + opps + '</div></div>' if opps else ''}

      <div class="signals-footer">Data collected: {signals}</div>
    </div>
    """


def render_html(analyses: list[dict], profile: dict, brand: dict, run_date: str) -> str:
    c = brand["colors"]
    logo_b64 = logo_as_base64()
    logo_tag = (
        f'<img src="data:image/png;base64,{logo_b64}" class="logo" alt="AIS Logo">'
        if logo_b64 else '<div class="logo-placeholder">AIS</div>'
    )

    company = profile.get("product_name", "AIS")
    total = len(analyses)
    high_threat = sum(1 for a in analyses if int(a.get("threat_level") or 0) >= 4)
    formatted_date = datetime.strptime(run_date, "%Y-%m-%d").strftime("%B %d, %Y")

    cards_html = "\n".join(render_competitor_card(a, brand) for a in analyses)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AIS Competitor Intelligence — {run_date}</title>
<style>
  :root {{
    --bg-primary: {c['bg_primary']};
    --bg-surface: {c['bg_surface']};
    --accent: {c['accent']};
    --text: {c['text_primary']};
    --muted: {c['text_muted']};
    --danger: {c['danger']};
    --warning: {c['warning']};
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: var(--bg-primary);
    color: var(--text);
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    padding: 0 0 60px 0;
  }}

  /* Header */
  .report-header {{
    background: var(--bg-surface);
    border-bottom: 3px solid var(--accent);
    padding: 28px 48px;
    display: flex;
    align-items: center;
    gap: 24px;
  }}
  .logo {{ height: 56px; width: auto; }}
  .logo-placeholder {{
    height: 56px; width: 56px;
    background: var(--accent);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 900; font-size: 20px; color: var(--bg-primary);
  }}
  .header-text {{ flex: 1; }}
  .header-title {{
    font-size: 22px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: 0.3px;
  }}
  .header-subtitle {{
    color: var(--accent);
    font-size: 13px;
    margin-top: 2px;
  }}
  .header-date {{
    color: var(--muted);
    font-size: 12px;
    margin-top: 4px;
  }}

  /* Summary bar */
  .summary-bar {{
    display: flex;
    gap: 24px;
    padding: 20px 48px;
    background: color-mix(in srgb, var(--bg-surface) 60%, transparent);
    border-bottom: 1px solid color-mix(in srgb, var(--accent) 20%, transparent);
  }}
  .stat-card {{
    background: var(--bg-surface);
    border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
    border-radius: 8px;
    padding: 12px 20px;
    min-width: 140px;
  }}
  .stat-value {{
    font-size: 28px;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
  }}
  .stat-value.danger {{ color: var(--danger); }}
  .stat-label {{
    font-size: 11px;
    color: var(--muted);
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  /* Content */
  .content {{ padding: 32px 48px; }}
  .section-title {{
    font-size: 15px;
    font-weight: 700;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 20px;
    padding-bottom: 8px;
    border-bottom: 1px solid color-mix(in srgb, var(--accent) 25%, transparent);
  }}

  /* Competitor cards */
  .competitor-card {{
    background: var(--bg-surface);
    border: 1px solid color-mix(in srgb, var(--accent) 15%, transparent);
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 20px;
  }}
  .card-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
  }}
  .competitor-name {{
    font-size: 17px;
    font-weight: 700;
    color: var(--text);
  }}
  .competitor-url a {{
    color: var(--muted);
    font-size: 12px;
    text-decoration: none;
  }}
  .competitor-url a:hover {{ color: var(--accent); }}
  .threat-badge {{
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    font-weight: 700;
    color: var(--bg-primary);
    white-space: nowrap;
  }}

  .card-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 4px;
  }}
  .signal-block {{ }}
  .signal-label {{
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--muted);
    margin-bottom: 4px;
  }}
  .muted {{ color: var(--muted); font-size: 12px; margin-top: 2px; }}
  .opp-block {{
    margin-top: 12px;
    padding: 12px;
    background: color-mix(in srgb, var(--accent) 8%, transparent);
    border-left: 3px solid var(--accent);
    border-radius: 4px;
  }}
  .signals-footer {{
    margin-top: 12px;
    font-size: 11px;
    color: var(--muted);
    font-style: italic;
  }}

  /* Footer */
  .report-footer {{
    text-align: center;
    padding: 24px;
    color: var(--muted);
    font-size: 11px;
    border-top: 1px solid color-mix(in srgb, var(--accent) 15%, transparent);
    margin-top: 40px;
  }}

  @media print {{
    :root {{
      --bg-primary: #ffffff;
      --bg-surface: #f4f6f8;
      --accent: #007a60;
      --text: #111111;
      --muted: #555555;
      --danger: #c0392b;
      --warning: #b7770d;
    }}
    body {{
      background: #ffffff;
      color: #111111;
      font-size: 12px;
    }}
    .report-header {{
      background: #f4f6f8;
      border-bottom: 3px solid #007a60;
    }}
    .header-title {{ color: #111111; }}
    .header-subtitle {{ color: #007a60; }}
    .header-date {{ color: #555555; }}
    .summary-bar {{
      background: #f4f6f8;
      border-bottom: 1px solid #dde2e7;
    }}
    .stat-card {{
      background: #ffffff;
      border: 1px solid #dde2e7;
    }}
    .stat-value {{ color: #007a60; }}
    .stat-value.danger {{ color: #c0392b; }}
    .section-title {{ color: #007a60; border-bottom-color: #dde2e7; }}
    .competitor-card {{
      background: #ffffff;
      border: 1px solid #dde2e7;
      page-break-inside: avoid;
      box-shadow: none;
    }}
    .competitor-name {{ color: #111111; }}
    .threat-badge {{ color: #ffffff; }}
    .signal-label {{ color: #555555; }}
    .muted {{ color: #555555; }}
    .opp-block {{
      background: #f0faf7;
      border-left: 3px solid #007a60;
    }}
    .report-footer {{
      color: #555555;
      border-top-color: #dde2e7;
    }}
    .competitor-url a {{ color: #555555; }}
  }}
</style>
</head>
<body>

<div class="report-header">
  {logo_tag}
  <div class="header-text">
    <div class="header-title">Competitor Intelligence Report</div>
    <div class="header-subtitle">{company} — Market Analysis</div>
    <div class="header-date">Generated: {formatted_date}</div>
  </div>
</div>

<div class="summary-bar">
  <div class="stat-card">
    <div class="stat-value">{total}</div>
    <div class="stat-label">Competitors Tracked</div>
  </div>
  <div class="stat-card">
    <div class="stat-value danger">{high_threat}</div>
    <div class="stat-label">High Threat (4-5)</div>
  </div>
  <div class="stat-card">
    <div class="stat-value">{run_date}</div>
    <div class="stat-label">Report Date</div>
  </div>
</div>

<div class="content">
  <div class="section-title">Competitor Profiles — Ranked by Threat Level</div>
  {cards_html}
</div>

<div class="report-footer">
  {brand.get('report_footer', 'Confidential — AIS Internal Use Only')}
  &nbsp;·&nbsp; Generated by AIS Competitor Intelligence Workflow
  &nbsp;·&nbsp; {formatted_date}
</div>

</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Generate branded AIS HTML competitor report")
    parser.add_argument("--run-date", required=True, help="Run date (YYYY-MM-DD)")
    parser.add_argument("--data-dir", default=".tmp", help="Directory containing *_analysis.json files")
    args = parser.parse_args()

    brand = load_brand()
    profile = load_profile()
    analyses = load_analyses(args.data_dir)

    if not analyses:
        print(f"No analysis files found in {args.data_dir}")
        return

    out_dir = DATA_DIR / "runs" / args.run_date
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"competitor_report_{args.run_date}.html"

    html = render_html(analyses, profile, brand, args.run_date)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] AIS branded report written to {out_path}")
    print(f"  Open in browser, then File > Print > Save as PDF for a PDF version")


if __name__ == "__main__":
    main()
