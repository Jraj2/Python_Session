"""
Synthesizes research JSON into a newsletter using Claude, renders via Jinja2, inlines CSS with Premailer.
Usage:
  python tools/generate_newsletter_html.py --research .tmp/research_xxx.json
  python tools/generate_newsletter_html.py --research .tmp/research_xxx.json --charts .tmp/chart_manifest.json --issue 3
Saves rendered HTML to .tmp/newsletter_{timestamp}.html and prints the path.
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import anthropic
from typing import Optional
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from premailer import transform

load_dotenv()

ROOT = Path(__file__).parent.parent
TMP = ROOT / ".tmp"
TEMPLATES_DIR = Path(__file__).parent / "templates"

NEWSLETTER_NAME = "The Signal"
REPLY_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "hello@example.com")
SENDER_ADDRESS = "Sent with care. No spam, ever."


SYNTHESIS_PROMPT = """You are a professional newsletter writer. Your job is to synthesize the research below into a compelling, well-structured newsletter issue.

Topic: {topic}
Issue Number: {issue_number}
Date: {date}

Research sources:
{sources_text}

{charts_context}

Return a JSON object ONLY (no markdown, no explanation) with this exact structure:
{{
  "subject": "Compelling email subject line (max 60 chars)",
  "tagline": "One-sentence hook for the header (max 90 chars)",
  "intro": "2-3 sentence engaging intro paragraph that sets context",
  "stories": [
    {{
      "tag": "SHORT CATEGORY TAG (e.g. RESEARCH, TREND, TOOLS, OPINION)",
      "headline": "Story headline (max 70 chars)",
      "body": "2-3 paragraph story body synthesized from the research. Be specific, cite facts. ~120-180 words.",
      "source_url": "URL of primary source",
      "source_title": "Title of primary source",
      "chart_url": null,
      "chart_caption": null,
      "takeaway": "One bold insight or actionable takeaway (1-2 sentences)"
    }}
  ],
  "closing": "Brief, warm closing paragraph (2-3 sentences). Invite reply or feedback.",
  "read_time": 4
}}

Rules:
- Write 3-5 stories. Each should cover a distinct angle from the research.
- Do not fabricate statistics not present in the research.
- Keep the tone smart, clear, and human — not corporate.
- If chart_url values are provided in the charts context, assign them to the most relevant story.
"""


def build_sources_text(sources: list) -> str:
    lines = []
    for i, s in enumerate(sources, 1):
        lines.append(f"[{i}] {s['title']}\nURL: {s['url']}\n{s['content'][:800]}\n")
    return "\n".join(lines)


def build_charts_context(charts: list) -> str:
    if not charts:
        return "No charts for this issue. Set chart_url to null in all stories."
    lines = ["Available chart images (assign to the most relevant story):"]
    for c in charts:
        lines.append(f"  - URL: {c['url']}  |  Caption: {c.get('caption', '')}")
    return "\n".join(lines)


def synthesize(research: dict, charts: list, issue_number: int) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY not set in .env")

    client = anthropic.Anthropic(api_key=api_key)
    date_str = datetime.utcnow().strftime("%B %d, %Y")
    sources_text = build_sources_text(research.get("sources", []))
    charts_context = build_charts_context(charts)

    prompt = SYNTHESIS_PROMPT.format(
        topic=research.get("topic", ""),
        issue_number=issue_number,
        date=date_str,
        sources_text=sources_text,
        charts_context=charts_context,
    )

    print("Calling Claude to synthesize newsletter content...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if Claude wrapped the JSON
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def render(newsletter_data: dict, issue_number: int) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)
    template = env.get_template("newsletter.html")

    date_str = datetime.utcnow().strftime("%B %d, %Y")
    html = template.render(
        newsletter_name=NEWSLETTER_NAME,
        subject=newsletter_data["subject"],
        tagline=newsletter_data["tagline"],
        issue_number=issue_number,
        issue_date=date_str,
        read_time=newsletter_data.get("read_time", 4),
        intro=newsletter_data["intro"],
        stories=newsletter_data["stories"],
        closing=newsletter_data["closing"],
        unsubscribe_url="-unsubscribe_link-",  # SendGrid substitution token
        reply_email=REPLY_EMAIL,
        sender_address=SENDER_ADDRESS,
    )
    # Inline all CSS for email client compatibility
    return transform(html)


def generate(research_path: Path, charts_path: Optional[Path], issue_number: int) -> Path:
    research = json.loads(research_path.read_text())
    charts = json.loads(charts_path.read_text()) if charts_path and charts_path.exists() else []

    newsletter_data = synthesize(research, charts, issue_number)

    html = render(newsletter_data, issue_number)

    TMP.mkdir(exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = TMP / f"newsletter_{ts}.html"
    out_path.write_text(html, encoding="utf-8")

    # Save metadata alongside HTML for reference
    meta_path = TMP / f"newsletter_{ts}_meta.json"
    meta_path.write_text(json.dumps(newsletter_data, indent=2, ensure_ascii=False))

    print(f"Newsletter rendered → {out_path}")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, help="Path to research JSON file")
    parser.add_argument("--charts", help="Path to chart manifest JSON (optional)")
    parser.add_argument("--issue", type=int, default=1, help="Issue number")
    args = parser.parse_args()

    research_path = Path(args.research)
    charts_path = Path(args.charts) if args.charts else None

    if not research_path.exists():
        sys.exit(f"Research file not found: {research_path}")

    out = generate(research_path, charts_path, args.issue)
    print(out)
