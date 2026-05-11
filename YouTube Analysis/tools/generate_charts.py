"""
Generate Matplotlib charts from YouTube niche analysis data.
Usage: python tools/generate_charts.py
Output: .tmp/charts/*.png (7 charts)
"""

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = Path(__file__).parent.parent
TMP_DIR = BASE_DIR / ".tmp"
CHARTS_DIR = TMP_DIR / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

# Brand palette (matches existing AIS brand)
BG = "#1A1E22"
ACCENT = "#00C9A0"
BLUE = "#4d96ff"
TEXT = "#FFFFFF"
SUBTEXT = "#AAAAAA"
GRID = "#2A2E32"
CARD = "#1E262E"

TOPIC_COLORS = [ACCENT, BLUE, "#ff6b6b", "#ffd93d", "#6bcb77",
                "#ff922b", "#cc5de8", "#20c997", "#f06595", "#74c0fc"]


def style_ax(fig, ax):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)
    for spine in ax.spines.values():
        spine.set_color(GRID)


def save(fig, name: str) -> str:
    out = CHARTS_DIR / name
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    return str(out)


# ── Chart 1: Top channels by subscriber count ────────────────────────────────

def chart_top_channels_subs(channels: list) -> str:
    top = sorted(channels, key=lambda c: c["subscriber_count"], reverse=True)[:10]
    names = [c["title"][:28] for c in top]
    subs = [c["subscriber_count"] / 1_000_000 for c in top]

    fig, ax = plt.subplots(figsize=(10, 6))
    style_ax(fig, ax)
    bars = ax.barh(names[::-1], subs[::-1], color=ACCENT, height=0.6, edgecolor=BG)
    ax.set_xlabel("Subscribers (millions)", color=TEXT)
    ax.set_title("Top 10 AI Channels — Subscriber Count", color=TEXT, fontsize=13, pad=12)
    ax.grid(axis="x", color=GRID, linestyle="--", alpha=0.5)
    for bar, val in zip(bars, subs[::-1]):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}M", va="center", color=TEXT, fontsize=8)
    plt.tight_layout()
    return save(fig, "top_channels_subscribers.png")


# ── Chart 2: Top channels by engagement rate ─────────────────────────────────

def chart_top_channels_engagement(channels: list, videos: list) -> str:
    ch_eng = defaultdict(list)
    for v in videos:
        if v["view_count"] >= 1000:
            ch_eng[v["channel_id"]].append(v["engagement_rate"])

    ch_map = {c["id"]: c["title"] for c in channels}
    ch_avg = {
        cid: sum(rates) / len(rates) * 100
        for cid, rates in ch_eng.items() if len(rates) >= 3
    }
    top = sorted(ch_avg.items(), key=lambda x: x[1], reverse=True)[:10]
    names = [ch_map.get(cid, cid)[:28] for cid, _ in top]
    rates = [r for _, r in top]
    colors = [ACCENT if i == 0 else BLUE for i in range(len(names))]

    fig, ax = plt.subplots(figsize=(10, 6))
    style_ax(fig, ax)
    bars = ax.barh(names[::-1], rates[::-1], color=colors[::-1], height=0.6, edgecolor=BG)
    ax.set_xlabel("Avg Engagement Rate (%)", color=TEXT)
    ax.set_title("Top 10 AI Channels — Engagement Rate", color=TEXT, fontsize=13, pad=12)
    ax.grid(axis="x", color=GRID, linestyle="--", alpha=0.5)
    for bar, val in zip(bars, rates[::-1]):
        ax.text(bar.get_width() + 0.003, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}%", va="center", color=TEXT, fontsize=8)
    plt.tight_layout()
    return save(fig, "top_channels_engagement.png")


# ── Chart 3: Top videos by view count ────────────────────────────────────────

def chart_top_videos_views(videos: list) -> str:
    top = sorted(videos, key=lambda v: v["view_count"], reverse=True)[:10]
    titles = [f"{v['title'][:38]}…" if len(v["title"]) > 38 else v["title"] for v in top]
    views = [v["view_count"] / 1_000_000 for v in top]

    fig, ax = plt.subplots(figsize=(11, 6))
    style_ax(fig, ax)
    bars = ax.barh(titles[::-1], views[::-1], color=ACCENT, height=0.6, edgecolor=BG)
    ax.set_xlabel("Views (millions)", color=TEXT)
    ax.set_title("Top 10 Most-Viewed AI Videos", color=TEXT, fontsize=13, pad=12)
    ax.grid(axis="x", color=GRID, linestyle="--", alpha=0.5)
    for bar, val in zip(bars, views[::-1]):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}M", va="center", color=TEXT, fontsize=8)
    plt.tight_layout()
    return save(fig, "top_videos_views.png")


# ── Chart 4: Topic distribution pie ──────────────────────────────────────────

def chart_topic_distribution(analysis: dict):
    clusters = analysis.get("topic_clusters", [])
    if not clusters:
        return None

    labels = [c["topic"] for c in clusters]
    sizes = [max(c["video_count"], 1) for c in clusters]
    colors = TOPIC_COLORS[:len(labels)]

    fig, ax = plt.subplots(figsize=(9, 7))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    wedges, _, autotexts = ax.pie(
        sizes, labels=None, colors=colors,
        autopct="%1.0f%%", startangle=140,
        pctdistance=0.82,
        wedgeprops={"linewidth": 1.5, "edgecolor": BG},
    )
    for at in autotexts:
        at.set_color(BG)
        at.set_fontsize(8)
        at.set_fontweight("bold")
    ax.legend(wedges, labels, loc="lower center", bbox_to_anchor=(0.5, -0.18),
              ncol=2, fontsize=8, framealpha=0, labelcolor=TEXT)
    ax.set_title("Content Topic Distribution in AI Niche", color=TEXT, fontsize=13, pad=16)
    plt.tight_layout()
    return save(fig, "topic_distribution.png")


# ── Chart 5: Video length vs views scatter ───────────────────────────────────

def chart_length_vs_views(videos: list) -> str:
    filtered = [
        v for v in videos
        if 0 < v["duration_seconds"] < 7200 and v["view_count"] > 0
    ]
    x = [v["duration_seconds"] / 60 for v in filtered]
    y = [v["view_count"] / 1000 for v in filtered]
    eng = [v["engagement_rate"] for v in filtered]

    fig, ax = plt.subplots(figsize=(10, 6))
    style_ax(fig, ax)
    sc = ax.scatter(x, y, c=eng, cmap="RdYlGn", alpha=0.6, s=25,
                    vmin=0, vmax=max(eng) if eng else 0.05)
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Engagement Rate", color=TEXT, fontsize=9)
    cbar.ax.yaxis.set_tick_params(labelcolor=TEXT)
    ax.set_xlabel("Video Length (minutes)", color=TEXT)
    ax.set_ylabel("Views (thousands)", color=TEXT)
    ax.set_title("Video Length vs. Views  (color = engagement rate)", color=TEXT, fontsize=13, pad=12)
    ax.grid(color=GRID, linestyle="--", alpha=0.4)
    plt.tight_layout()
    return save(fig, "video_length_vs_views.png")


# ── Chart 6: Upload frequency (last 12 weeks) ────────────────────────────────

def chart_upload_frequency(videos: list) -> str:
    from collections import Counter
    now = datetime.now(timezone.utc)
    week_counts = Counter()
    for v in videos:
        pub = v.get("published_at", "")
        if not pub:
            continue
        try:
            dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            weeks_ago = int((now - dt).days / 7)
            if 0 <= weeks_ago < 12:
                week_counts[weeks_ago] += 1
        except ValueError:
            continue

    weeks = list(range(11, -1, -1))
    counts = [week_counts.get(w, 0) for w in weeks]
    labels = [f"{w}w ago" if w > 0 else "This\nweek" for w in weeks]

    fig, ax = plt.subplots(figsize=(12, 5))
    style_ax(fig, ax)
    bars = ax.bar(labels, counts, color=ACCENT, width=0.6, edgecolor=BG)
    ax.set_ylabel("Videos Published", color=TEXT)
    ax.set_title("AI Niche Upload Velocity — Last 12 Weeks", color=TEXT, fontsize=13, pad=12)
    ax.grid(axis="y", color=GRID, linestyle="--", alpha=0.5)
    plt.xticks(rotation=30, ha="right", fontsize=8)
    for bar, val in zip(bars, counts):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    str(val), ha="center", va="bottom", color=TEXT, fontsize=8)
    plt.tight_layout()
    return save(fig, "upload_frequency.png")


# ── Chart 7: Engagement rate by topic cluster ────────────────────────────────

def chart_engagement_by_topic(analysis: dict):
    clusters = analysis.get("topic_clusters", [])
    if not clusters:
        return None

    sorted_c = sorted(clusters, key=lambda c: c.get("avg_engagement_rate", 0), reverse=True)
    topics = [c["topic"][:22] for c in sorted_c]
    rates = [c.get("avg_engagement_rate", 0) * 100 for c in sorted_c]
    max_r = max(rates) if rates else 1
    colors = [ACCENT if r == max_r else BLUE for r in rates]

    fig, ax = plt.subplots(figsize=(10, 5))
    style_ax(fig, ax)
    bars = ax.bar(topics, rates, color=colors, width=0.6, edgecolor=BG)
    ax.set_ylabel("Avg Engagement Rate (%)", color=TEXT)
    ax.set_title("Engagement Rate by Topic Cluster", color=TEXT, fontsize=13, pad=12)
    ax.grid(axis="y", color=GRID, linestyle="--", alpha=0.5)
    plt.xticks(rotation=20, ha="right", fontsize=8)
    for bar, val in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
                f"{val:.2f}%", ha="center", va="bottom", color=TEXT, fontsize=7)
    plt.tight_layout()
    return save(fig, "engagement_by_topic.png")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    for fname in ["channels.json", "videos.json", "analysis.json"]:
        if not (TMP_DIR / fname).exists():
            print(f"ERROR: .tmp/{fname} not found. Run previous pipeline steps first.")
            return

    with open(TMP_DIR / "channels.json", encoding="utf-8") as f:
        channels = json.load(f)["channels"]
    with open(TMP_DIR / "videos.json", encoding="utf-8") as f:
        videos = json.load(f)["videos"]
    with open(TMP_DIR / "analysis.json", encoding="utf-8") as f:
        analysis = json.load(f)

    chart_defs = [
        ("Top Channels (Subscribers)", chart_top_channels_subs, [channels]),
        ("Top Channels (Engagement)", chart_top_channels_engagement, [channels, videos]),
        ("Top Videos (Views)", chart_top_videos_views, [videos]),
        ("Topic Distribution", chart_topic_distribution, [analysis]),
        ("Video Length vs Views", chart_length_vs_views, [videos]),
        ("Upload Frequency", chart_upload_frequency, [videos]),
        ("Engagement by Topic", chart_engagement_by_topic, [analysis]),
    ]

    print("Generating charts...")
    generated = []
    for name, fn, args in chart_defs:
        try:
            out = fn(*args)
            if out:
                print(f"  [OK] {name} -> {Path(out).name}")
                generated.append(out)
            else:
                print(f"  [SKIP] {name} — no data available")
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")

    print(f"\n[OK] {len(generated)} charts saved to .tmp/charts/")


if __name__ == "__main__":
    main()
