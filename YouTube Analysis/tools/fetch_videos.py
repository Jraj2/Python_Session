"""
Fetch recent videos and engagement metrics for each channel in .tmp/channels.json.
Usage: python tools/fetch_videos.py
Output: .tmp/videos.json
Quota cost: ~600 units for 50 channels × 20 videos
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
TMP_DIR = BASE_DIR / ".tmp"

VIDEOS_PER_CHANNEL = 20


def get_youtube_client():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY not set in .env")
    return build("youtube", "v3", developerKey=api_key)


def iso8601_to_seconds(duration: str) -> int:
    """Convert ISO 8601 duration (e.g. PT4M13S) to total seconds."""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration or "")
    if not match:
        return 0
    h = int(match.group(1) or 0)
    m = int(match.group(2) or 0)
    s = int(match.group(3) or 0)
    return h * 3600 + m * 60 + s


def fetch_playlist_video_ids(youtube, playlist_id: str, max_results: int = 20) -> list:
    """Return video IDs from a channel's uploads playlist."""
    response = youtube.playlistItems().list(
        playlistId=playlist_id,
        part="contentDetails",
        maxResults=max_results,
    ).execute()
    return [item["contentDetails"]["videoId"] for item in response.get("items", [])]


def fetch_video_details(youtube, video_ids: list) -> list:
    """Batch-fetch video metadata and stats (50 IDs per request)."""
    videos = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        response = youtube.videos().list(
            id=",".join(batch),
            part="id,snippet,statistics,contentDetails",
        ).execute()
        for item in response.get("items", []):
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            content = item.get("contentDetails", {})

            view_count = int(stats.get("viewCount", 0))
            like_count = int(stats.get("likeCount", 0))
            comment_count = int(stats.get("commentCount", 0))
            duration_secs = iso8601_to_seconds(content.get("duration", ""))
            engagement_rate = round(
                (like_count + comment_count) / view_count if view_count > 0 else 0, 4
            )

            videos.append({
                "id": item["id"],
                "title": snippet.get("title", ""),
                "description": snippet.get("description", "")[:300],
                "channel_id": snippet.get("channelId", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "tags": snippet.get("tags", [])[:10],
                "duration_seconds": duration_secs,
                "view_count": view_count,
                "like_count": like_count,
                "comment_count": comment_count,
                "engagement_rate": engagement_rate,
            })
    return videos


def main():
    channels_path = TMP_DIR / "channels.json"
    if not channels_path.exists():
        print("ERROR: .tmp/channels.json not found. Run fetch_channels.py first.")
        return

    with open(channels_path, encoding="utf-8") as f:
        data = json.load(f)
    channels = data["channels"]

    youtube = get_youtube_client()
    all_videos = []

    print(f"Fetching up to {VIDEOS_PER_CHANNEL} videos for each of {len(channels)} channels...")
    for i, channel in enumerate(channels, 1):
        playlist_id = channel.get("uploads_playlist_id")
        if not playlist_id:
            safe = channel['title'].encode('ascii', 'replace').decode()
            print(f"  [{i:02d}/{len(channels)}] SKIP {safe} — no playlist ID")
            continue
        try:
            video_ids = fetch_playlist_video_ids(youtube, playlist_id, VIDEOS_PER_CHANNEL)
            videos = fetch_video_details(youtube, video_ids)
            all_videos.extend(videos)
            safe = channel['title'].encode('ascii', 'replace').decode()
            print(f"  [{i:02d}/{len(channels)}] {safe} — {len(videos)} videos fetched")
        except Exception as e:
            safe = channel['title'].encode('ascii', 'replace').decode()
            print(f"  [{i:02d}/{len(channels)}] ERROR {safe}: {e}")

    output = {
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "total_videos": len(all_videos),
        "videos": all_videos,
    }

    out_path = TMP_DIR / "videos.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] {len(all_videos)} videos saved to {out_path}")
    top = sorted(all_videos, key=lambda v: v["view_count"], reverse=True)[:3]
    print("Top 3 by views:")
    for v in top:
        safe_title = v['title'].encode('ascii', 'replace').decode()
        print(f"  {v['view_count']:,} views — \"{safe_title}\"")


if __name__ == "__main__":
    main()
