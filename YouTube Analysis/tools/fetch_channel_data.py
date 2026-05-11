"""
Fetch a single YouTube channel's snapshot + 50 most recent videos.
Usage:
    python tools/fetch_channel_data.py --channel "@mkbhd"
    python tools/fetch_channel_data.py --channel UCBJycsmduvYEL83R_U4JriQ
Output: .tmp/channel_<ID>.json
Quota cost: ~5 units per run.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
TMP_DIR = BASE_DIR / ".tmp"
TMP_DIR.mkdir(exist_ok=True)

VIDEOS_TO_FETCH = 50


def get_youtube_client():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY not set in .env")
    return build("youtube", "v3", developerKey=api_key)


def iso8601_to_seconds(duration: str) -> int:
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration or "")
    if not match:
        return 0
    h = int(match.group(1) or 0)
    m = int(match.group(2) or 0)
    s = int(match.group(3) or 0)
    return h * 3600 + m * 60 + s


def resolve_channel(youtube, identifier: str) -> dict:
    """Accept a channel ID, @handle, or plain custom slug; return channel record."""
    identifier = identifier.strip()

    # Direct channel ID
    if identifier.startswith("UC") and len(identifier) >= 20:
        resp = youtube.channels().list(
            part="snippet,statistics,contentDetails",
            id=identifier,
        ).execute()
    # Handle (with or without leading @)
    elif identifier.startswith("@") or not identifier.startswith("UC"):
        handle = identifier if identifier.startswith("@") else "@" + identifier
        resp = youtube.channels().list(
            part="snippet,statistics,contentDetails",
            forHandle=handle,
        ).execute()
    else:
        raise ValueError(f"Unrecognized channel identifier: {identifier}")

    items = resp.get("items", [])
    if not items:
        raise ValueError(f"No channel found for: {identifier}")
    return items[0]


def fetch_recent_videos(youtube, uploads_playlist_id: str, max_videos: int) -> list:
    """Pull the most recent video IDs from the uploads playlist, then batch-fetch details."""
    video_ids = []
    page_token = None
    while len(video_ids) < max_videos:
        resp = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part="contentDetails",
            maxResults=min(50, max_videos - len(video_ids)),
            pageToken=page_token,
        ).execute()
        for item in resp.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    videos = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        resp = youtube.videos().list(
            id=",".join(batch),
            part="id,snippet,statistics,contentDetails",
        ).execute()
        for item in resp.get("items", []):
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            content = item.get("contentDetails", {})
            view_count = int(stats.get("viewCount", 0))
            like_count = int(stats.get("likeCount", 0))
            comment_count = int(stats.get("commentCount", 0))
            duration = iso8601_to_seconds(content.get("duration", ""))
            engagement_rate = round(
                (like_count + comment_count) / view_count if view_count > 0 else 0,
                4,
            )
            videos.append({
                "id": item["id"],
                "title": snippet.get("title", ""),
                "published_at": snippet.get("publishedAt", ""),
                "duration_seconds": duration,
                "is_short": duration > 0 and duration <= 60,
                "view_count": view_count,
                "like_count": like_count,
                "comment_count": comment_count,
                "engagement_rate": engagement_rate,
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            })
    # Newest first
    videos.sort(key=lambda v: v["published_at"], reverse=True)
    return videos


def build_record(channel: dict, videos: list) -> dict:
    snippet = channel.get("snippet", {})
    stats = channel.get("statistics", {})
    return {
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "channel": {
            "id": channel["id"],
            "title": snippet.get("title", ""),
            "handle": snippet.get("customUrl", ""),
            "description": snippet.get("description", "")[:500],
            "country": snippet.get("country", ""),
            "published_at": snippet.get("publishedAt", ""),
            "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "subscribers_hidden": stats.get("hiddenSubscriberCount", False),
            "total_views": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
        },
        "videos": videos,
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch a single YouTube channel's data.")
    parser.add_argument("--channel", required=True, help="Channel ID, @handle, or custom slug")
    parser.add_argument("--max-videos", type=int, default=VIDEOS_TO_FETCH)
    args = parser.parse_args()

    youtube = get_youtube_client()
    print(f"Resolving channel: {args.channel}")
    channel = resolve_channel(youtube, args.channel)
    channel_id = channel["id"]
    title = channel["snippet"].get("title", "(unknown)")
    safe_title = title.encode("ascii", "replace").decode()
    print(f"  -> {channel_id}  |  {safe_title}")

    uploads_playlist = channel.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
    if not uploads_playlist:
        print("ERROR: No uploads playlist found for this channel.")
        sys.exit(1)

    print(f"Fetching up to {args.max_videos} recent videos...")
    videos = fetch_recent_videos(youtube, uploads_playlist, args.max_videos)
    print(f"  -> {len(videos)} videos retrieved")

    record = build_record(channel, videos)
    out_path = TMP_DIR / f"channel_{channel_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Saved -> {out_path}")
    subs = record["channel"]["subscriber_count"]
    subs_str = "Hidden" if record["channel"]["subscribers_hidden"] else f"{subs:,}"
    print(f"  Subscribers: {subs_str}  |  Total views: {record['channel']['total_views']:,}")


if __name__ == "__main__":
    main()
