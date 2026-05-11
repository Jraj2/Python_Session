"""
Send aggregated competitor signals to Claude and return structured analysis JSON.
Usage: python analyze_competitor.py --competitor-json .tmp/<name>_signals.json
Output: writes .tmp/<name>_analysis.json
"""

import argparse
import json
import os
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# JSON schema Claude must match exactly
OUTPUT_SCHEMA = {
    "competitor_name": "string",
    "run_date": "YYYY-MM-DD",
    "messaging_summary": "2-3 sentence summary of their positioning and key messages",
    "pricing_tier": "Free | Freemium | Under $50/mo | $50-200/mo | $200+/mo | Enterprise | Unknown",
    "pricing_notes": "specific plan names, price points, or notable pricing signals found",
    "review_sentiment": "Positive | Mixed | Negative | Insufficient data",
    "avg_rating": "numeric 1-5 or null",
    "top_review_theme": "most common praise or complaint in 10 words or less",
    "active_job_count": "integer",
    "key_hiring_areas": ["list", "of", "departments"],
    "threat_level": "integer 1-5 (1=minimal, 5=high direct threat to AIS)",
    "threat_rationale": "one sentence explaining the threat level score",
    "notable_changes": "what changed since the prior analysis, or 'First analysis' if no prior data",
    "signals_available": ["list of signals that had data: website, pricing, reviews, jobs"],
    "opportunities_for_ais": "2-3 specific gaps or weaknesses in this competitor that AIS could exploit",
}

SYSTEM_PROMPT = """You are a senior competitive intelligence analyst for AIS, an early-stage SaaS company \
in the competitor analysis and market intelligence space.

Your job: analyze raw data about a competitor and return a structured JSON report.

CRITICAL RULES:
1. Return ONLY valid JSON matching the schema below — no preamble, no explanation, no markdown fences.
2. Be specific and factual. If data is missing for a field, use null or "Insufficient data".
3. Threat level rubric:
   - 1: Not a real competitor or operates in a different segment
   - 2: Indirect competitor, minimal overlap
   - 3: Moderate overlap, worth watching
   - 4: Direct competitor with strong positioning
   - 5: Strong direct competitor that actively targets AIS's exact market

OUTPUT SCHEMA (return JSON matching this exactly):
""" + json.dumps(OUTPUT_SCHEMA, indent=2)


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_prior_analysis(competitor_name: str) -> dict | None:
    """Find the most recent prior analysis for this competitor."""
    runs_dir = DATA_DIR / "runs"
    if not runs_dir.exists():
        return None

    run_dates = sorted(
        [d for d in runs_dir.iterdir() if d.is_dir()],
        reverse=True,
    )
    safe_name = competitor_name.lower().replace(" ", "_").replace("/", "_")
    for run_dir in run_dates:
        analysis_path = run_dir / f"{safe_name}_analysis.json"
        if analysis_path.exists():
            return load_json(str(analysis_path))
    return None


def build_user_message(signals: dict, profile: dict, prior: dict | None) -> str:
    parts = []

    parts.append("[BUSINESS PROFILE — AIS]")
    parts.append(json.dumps(profile, indent=2))

    parts.append("\n[COMPETITOR OVERVIEW]")
    parts.append(f"Name: {signals.get('competitor_name', 'Unknown')}")
    parts.append(f"Website: {signals.get('website_url', 'Unknown')}")
    parts.append(f"Run date: {signals.get('run_date', 'Unknown')}")

    website = signals.get("website", {})
    if website and not website.get("error"):
        parts.append("\n[WEBSITE & MESSAGING]")
        parts.append(f"Title: {website.get('title', '')}")
        parts.append(f"Meta: {website.get('meta_description', '')}")
        parts.append(f"Body (excerpt): {website.get('body_text', '')[:3000]}")
    else:
        parts.append("\n[WEBSITE & MESSAGING]\nData unavailable.")

    pricing = signals.get("pricing", {})
    if pricing and not pricing.get("error"):
        parts.append("\n[PRICING PAGE]")
        parts.append(f"Body (excerpt): {pricing.get('body_text', '')[:2000]}")
    else:
        parts.append("\n[PRICING PAGE]\nData unavailable.")

    reviews = signals.get("reviews", {})
    review_list = reviews.get("reviews", []) if reviews else []
    if review_list:
        parts.append(f"\n[CUSTOMER REVIEWS] ({len(review_list)} found)")
        for r in review_list[:10]:
            rating_str = f" [{r.get('rating')}/5]" if r.get("rating") else ""
            parts.append(f"- [{r.get('source', '?')}]{rating_str} {r.get('text', '')}")
    else:
        parts.append("\n[CUSTOMER REVIEWS]\nData unavailable.")

    jobs = signals.get("jobs", {})
    job_list = jobs.get("jobs", []) if jobs else []
    if job_list:
        parts.append(f"\n[JOB POSTINGS] ({len(job_list)} found)")
        for j in job_list[:20]:
            dept = f" [{j.get('department')}]" if j.get("department") else ""
            parts.append(f"- {j.get('title', '')}{dept}")
    else:
        parts.append("\n[JOB POSTINGS]\nData unavailable.")

    if prior:
        parts.append("\n[PRIOR ANALYSIS — last week]")
        parts.append(f"Threat level was: {prior.get('threat_level')}")
        parts.append(f"Prior messaging: {prior.get('messaging_summary', '')}")
        parts.append(f"Prior pricing: {prior.get('pricing_tier')} — {prior.get('pricing_notes', '')}")
    else:
        parts.append("\n[PRIOR ANALYSIS]\nFirst analysis — no prior data.")

    return "\n".join(parts)


def call_claude(user_message: str, retry: bool = False) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")

    extra_note = "\n\nIMPORTANT: Return ONLY valid JSON, nothing else." if retry else ""

    response = client.messages.create(
        model=model,
        max_tokens=1500,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT + extra_note,
                # Cache the system prompt — it's identical across all competitor calls in a run
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {"role": "user", "content": user_message},
            # Prefill to force JSON output
            {"role": "assistant", "content": "{"},
        ],
    )

    raw = "{" + response.content[0].text.strip()
    # Strip markdown code fences if present
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.split("```")[0]

    return json.loads(raw.strip())


def main():
    parser = argparse.ArgumentParser(description="Analyze competitor signals with Claude")
    parser.add_argument("--competitor-json", required=True, help="Path to .tmp/<name>_signals.json")
    args = parser.parse_args()

    signals = load_json(args.competitor_json)
    competitor_name = signals.get("competitor_name", "unknown")

    profile_path = DATA_DIR / "business_profile.json"
    profile = load_json(str(profile_path)) if profile_path.exists() else {}

    prior = find_prior_analysis(competitor_name)

    user_message = build_user_message(signals, profile, prior)

    print(f"  Analyzing {competitor_name} with Claude...")
    try:
        result = call_claude(user_message)
    except (json.JSONDecodeError, Exception) as e:
        print(f"  First attempt failed ({e}). Retrying...")
        time.sleep(3)
        try:
            result = call_claude(user_message, retry=True)
        except Exception as e2:
            # Write parse error placeholder
            out_path = Path(args.competitor_json).parent / f"{competitor_name.lower().replace(' ', '_')}_analysis.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump({"competitor_name": competitor_name, "parse_error": str(e2)}, f)
            print(f"  ERROR: Could not parse Claude response. Placeholder written.")
            return

    # Determine output path from input path
    input_path = Path(args.competitor_json)
    safe_name = competitor_name.lower().replace(" ", "_").replace("/", "_")
    out_path = input_path.parent / f"{safe_name}_analysis.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"  [OK] Analysis written to {out_path}")
    print(f"    Threat level: {result.get('threat_level')}/5 — {result.get('threat_rationale', '')}")


if __name__ == "__main__":
    main()
