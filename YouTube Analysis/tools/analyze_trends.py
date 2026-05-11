"""
Analyze YouTube niche data with Claude to surface trending topics, title patterns,
content gaps, and strategy recommendations.
Usage: python tools/analyze_trends.py
Output: .tmp/analysis.json
"""

import json
import os
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
TMP_DIR = BASE_DIR / ".tmp"

OUTPUT_SCHEMA = {
    "run_date": "YYYY-MM-DD",
    "channels_analyzed": "integer",
    "videos_analyzed": "integer",
    "top_channels_by_engagement": [
        {"channel_title": "string", "engagement_rate": "float", "subscriber_count": "integer"}
    ],
    "topic_clusters": [
        {
            "topic": "string (e.g. AI Agents, LLM Tutorials, Tool Reviews, AI News)",
            "video_count": "integer",
            "avg_engagement_rate": "float",
            "example_titles": ["up to 3 representative video titles"],
        }
    ],
    "title_patterns": [
        {
            "pattern": "string describing the format/hook (e.g. 'How I [action] with [tool] in [timeframe]')",
            "why_it_works": "1-sentence explanation grounded in the data",
            "example": "a specific title from the dataset that uses this pattern",
        }
    ],
    "content_gaps": [
        {
            "gap": "specific under-covered topic or angle in the current dataset",
            "opportunity": "1-sentence explanation of why this is worth covering now",
        }
    ],
    "trending_keywords": ["list of 10 keywords/phrases appearing frequently in high-performing titles"],
    "optimal_video_length": "string describing the sweet spot length range with supporting data",
    "upload_frequency_insight": "string describing how often top channels post and what pattern correlates with growth",
    "recommendations": [
        {
            "action": "specific content action (e.g. 'Create a beginner guide to AI agents using n8n')",
            "rationale": "why this will drive views and engagement based on the data",
        }
    ],
    "executive_summary": "3-4 sentence high-level summary of the state of the AI YouTube niche right now",
}

SYSTEM_PROMPT = (
    "You are a YouTube content strategist specializing in the AI and AI automation niche.\n\n"
    "Your job: analyze channel and video data from YouTube to surface actionable content intelligence "
    "for a creator building their presence in the AI space.\n\n"
    "CRITICAL RULES:\n"
    "1. Return ONLY valid JSON matching the schema — no preamble, no markdown fences.\n"
    "2. Base every insight on the actual data provided — no generic advice.\n"
    "3. Engagement rate = (likes + comments) / views. High engagement beats high views.\n"
    "4. Identify what's actually working in the data, not just what's popular.\n"
    "5. Be specific: name actual tools, channels, topics from the data.\n\n"
    "OUTPUT SCHEMA:\n"
    + json.dumps(OUTPUT_SCHEMA, indent=2)
)


def build_user_message(channels: list, videos: list) -> str:
    parts = []

    # Top channels by subscribers
    top_channels = sorted(channels, key=lambda c: c["subscriber_count"], reverse=True)[:20]
    parts.append("[TOP 20 CHANNELS BY SUBSCRIBER COUNT]")
    for c in top_channels:
        parts.append(
            f"- {c['title']} | {c['subscriber_count']:,} subs | "
            f"{c['view_count']:,} total views | {c['video_count']} videos"
        )

    # Top videos by engagement rate (min 5k views to filter noise)
    qualified = [v for v in videos if v["view_count"] >= 5000]
    top_by_eng = sorted(qualified, key=lambda v: v["engagement_rate"], reverse=True)[:30]
    parts.append("\n[TOP 30 VIDEOS BY ENGAGEMENT RATE — minimum 5,000 views]")
    for v in top_by_eng:
        dur_min = v["duration_seconds"] // 60
        parts.append(
            f"- \"{v['title']}\" | {v['view_count']:,} views | "
            f"{v['engagement_rate']:.2%} engagement | {dur_min}min | {v['channel_title']}"
        )

    # Top videos by raw views
    top_by_views = sorted(videos, key=lambda v: v["view_count"], reverse=True)[:30]
    parts.append("\n[TOP 30 VIDEOS BY VIEW COUNT]")
    for v in top_by_views:
        dur_min = v["duration_seconds"] // 60
        parts.append(
            f"- \"{v['title']}\" | {v['view_count']:,} views | "
            f"{v['engagement_rate']:.2%} engagement | {dur_min}min | {v['channel_title']}"
        )

    # Recent 100 video titles (for trend spotting)
    recent = sorted(videos, key=lambda v: v.get("published_at", ""), reverse=True)[:100]
    parts.append("\n[100 MOST RECENT VIDEO TITLES]")
    for v in recent:
        parts.append(f"- \"{v['title']}\" ({v['channel_title']})")

    # Top tags/keywords
    all_tags = []
    for v in videos:
        all_tags.extend(v.get("tags", []))
    top_tags = Counter(all_tags).most_common(50)
    parts.append("\n[TOP 50 TAGS ACROSS ALL VIDEOS (tag: count)]")
    parts.append(", ".join(f"{tag}:{count}" for tag, count in top_tags))

    return "\n".join(parts)


def call_claude(user_message: str, retry: bool = False) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set — add it to .env or your Modal secret")
    client = anthropic.Anthropic(api_key=api_key)
    model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")

    extra = "\n\nIMPORTANT: Return ONLY valid JSON, nothing else." if retry else ""

    response = client.messages.create(
        model=model,
        max_tokens=4000,
        system=SYSTEM_PROMPT + extra,
        messages=[
            {"role": "user", "content": user_message + "\n\nRespond with ONLY a valid JSON object. No explanation, no markdown fences."},
        ],
    )

    raw = response.content[0].text.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.split("```")[0]
    return json.loads(raw.strip())


def main():
    for fname in ["channels.json", "videos.json"]:
        if not (TMP_DIR / fname).exists():
            print(f"ERROR: .tmp/{fname} not found. Run fetch scripts first.")
            return

    with open(TMP_DIR / "channels.json", encoding="utf-8") as f:
        channels = json.load(f)["channels"]
    with open(TMP_DIR / "videos.json", encoding="utf-8") as f:
        videos = json.load(f)["videos"]

    print(f"Sending {len(channels)} channels and {len(videos)} videos to Claude for analysis...")
    user_message = build_user_message(channels, videos)

    try:
        result = call_claude(user_message)
    except (json.JSONDecodeError, Exception) as e:
        print(f"  First attempt failed ({e}). Retrying in 3s...")
        time.sleep(3)
        result = call_claude(user_message, retry=True)

    result["run_date"] = datetime.utcnow().strftime("%Y-%m-%d")
    result["channels_analyzed"] = len(channels)
    result["videos_analyzed"] = len(videos)

    out_path = TMP_DIR / "analysis.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[OK] Analysis written to {out_path}")
    print(f"  Topic clusters: {len(result.get('topic_clusters', []))}")
    print(f"  Content gaps identified: {len(result.get('content_gaps', []))}")
    print(f"  Recommendations: {len(result.get('recommendations', []))}")
    print(f"\nSummary: {result.get('executive_summary', '')}")


if __name__ == "__main__":
    main()
