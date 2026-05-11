"""
Discover top YouTube channels in the AI/automation niche via YouTube Data API v3.
Usage: python tools/fetch_channels.py
Output: .tmp/channels.json
Quota cost: ~650 units
"""

import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
TMP_DIR = BASE_DIR / ".tmp"
TMP_DIR.mkdir(exist_ok=True)

SEED_KEYWORDS = [
    "AI automation tutorial",
    "artificial intelligence explained",
    "ChatGPT tips and tricks",
    "LLM tutorial 2024",
    "machine learning for beginners",
    "AI tools review",
]

MAX_CHANNELS_PER_KEYWORD = 10


def get_youtube_client():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY not set in .env")
    return build("youtube", "v3", developerKey=api_key)


def search_channels_by_keyword(youtube, keyword: str) -> list:
    """Return list of channel IDs matching a keyword search."""
    response = youtube.search().list(
        q=keyword,
        type="channel",
        part="id",
        maxResults=MAX_CHANNELS_PER_KEYWORD,
        order="viewCount",
    ).execute()
    return [item["id"]["channelId"] for item in response.get("items", [])]


def fetch_channel_details(youtube, channel_ids: list) -> list:
    """Batch-fetch channel stats and uploads playlist ID (50 IDs per request)."""
    channels = []
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i : i + 50]
        response = youtube.channels().list(
            id=",".join(batch),
            part="id,snippet,statistics,contentDetails",
        ).execute()
        for item in response.get("items", []):
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            content = item.get("contentDetails", {})
            channels.append({
                "id": item["id"],
                "title": snippet.get("title", ""),
                "description": snippet.get("description", "")[:500],
                "country": snippet.get("country", ""),
                "published_at": snippet.get("publishedAt", ""),
                "uploads_playlist_id": content.get("relatedPlaylists", {}).get("uploads", ""),
                "subscriber_count": int(stats.get("subscriberCount", 0)),
                "video_count": int(stats.get("videoCount", 0)),
                "view_count": int(stats.get("viewCount", 0)),
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            })
    return channels


def main():
    youtube = get_youtube_client()

    print("Searching for AI/automation channels...")
    all_channel_ids = set()
    for keyword in SEED_KEYWORDS:
        print(f"  Keyword: '{keyword}'")
        ids = search_channels_by_keyword(youtube, keyword)
        all_channel_ids.update(ids)
        print(f"    Found {len(ids)} channels ({len(all_channel_ids)} unique so far)")

    print(f"\nFetching stats for {len(all_channel_ids)} unique channels...")
    channels = fetch_channel_details(youtube, list(all_channel_ids))
    channels.sort(key=lambda c: c["subscriber_count"], reverse=True)

    output = {
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "keywords_used": SEED_KEYWORDS,
        "total_channels": len(channels),
        "channels": channels,
    }

    out_path = TMP_DIR / "channels.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] {len(channels)} channels saved to {out_path}")
    print("Top 5 by subscriber count:")
    for c in channels[:5]:
        print(f"  {c['title']} — {c['subscriber_count']:,} subscribers")


if __name__ == "__main__":
    main()
