"""
Build an 8-slide corporate-professional PPT for a single YouTube channel.

Usage:
    python tools/create_channel_ppt.py --channel "@mkbhd"
    python tools/create_channel_ppt.py --channel UCBJycsmduvYEL83R_U4JriQ \
        --history subscriber_history.csv

Reads:    .tmp/channel_<ID>.json   (produced by fetch_channel_data.py)
          subscriber_history.csv   (optional, two columns: date,subscribers)
Outputs:  .tmp/channel_<ID>_<YYYY-MM-DD>.pptx
          .tmp/channel_<ID>_charts/*.png

Three required charts:
  1. Views over time           — line chart  (monthly aggregate)
  2. Channel growth            — area chart  (subscribers if CSV given,
                                              otherwise cumulative views proxy)
  3. Top videos ranking        — horizontal bar (top 10 by views)
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

BASE_DIR = Path(__file__).parent.parent
TMP_DIR = BASE_DIR / ".tmp"

# ── Corporate Professional palette (Midnight Executive) ──────────────────────
C_NAVY      = RGBColor(0x1E, 0x27, 0x61)
C_NAVY_DEEP = RGBColor(0x14, 0x1B, 0x42)
C_ICE       = RGBColor(0xCA, 0xDC, 0xFC)
C_WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
C_GREY      = RGBColor(0x6B, 0x72, 0x80)
C_GREY_LIGHT = RGBColor(0xE6, 0xE9, 0xEF)
C_TEXT      = RGBColor(0x1F, 0x29, 0x37)
C_ACCENT    = RGBColor(0x4D, 0x7C, 0xFE)

MPL_NAVY = "#1E2761"
MPL_ICE = "#CADCFC"
MPL_ACCENT = "#4D7CFE"
MPL_GREY = "#6B7280"
MPL_GRID = "#E6E9EF"

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


# ── Number formatting ────────────────────────────────────────────────────────

def human_number(n: float) -> str:
    n = float(n)
    if abs(n) >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if abs(n) >= 1_000:
        return f"{n/1_000:.1f}K"
    return f"{int(n)}"


# ── Chart generation (matplotlib) ────────────────────────────────────────────

def style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(MPL_GREY)
    ax.spines["bottom"].set_color(MPL_GREY)
    ax.tick_params(colors=MPL_GREY)
    ax.yaxis.label.set_color(MPL_GREY)
    ax.xaxis.label.set_color(MPL_GREY)
    ax.grid(axis="y", color=MPL_GRID, linestyle="-", linewidth=0.7)
    ax.set_axisbelow(True)


def chart_views_over_time(videos: list, out_path: Path):
    """Monthly aggregate of view counts from the recent uploads, as a line chart."""
    monthly = defaultdict(int)
    for v in videos:
        if not v.get("published_at"):
            continue
        d = datetime.fromisoformat(v["published_at"].replace("Z", "+00:00"))
        key = datetime(d.year, d.month, 1)
        monthly[key] += v["view_count"]
    if not monthly:
        return
    months = sorted(monthly.keys())
    values = [monthly[m] for m in months]

    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=160)
    ax.plot(months, values, color=MPL_NAVY, linewidth=2.5, marker="o",
            markersize=6, markerfacecolor=MPL_ACCENT, markeredgecolor="white",
            markeredgewidth=1.5)
    ax.fill_between(months, values, color=MPL_ICE, alpha=0.45)
    style_axes(ax)
    ax.set_title("Total Views per Month (Recent Uploads)", color=MPL_NAVY,
                 fontsize=14, fontweight="bold", loc="left", pad=14)
    ax.set_ylabel("Views")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: human_number(x)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def chart_growth_area(videos: list, channel: dict, history_csv: Path, out_path: Path):
    """Area chart — real subscriber history if CSV provided, else cumulative views proxy."""
    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=160)

    if history_csv and history_csv.exists():
        dates, subs = [], []
        with open(history_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    dates.append(datetime.fromisoformat(row["date"]))
                    subs.append(int(row["subscribers"]))
                except (KeyError, ValueError):
                    continue
        if dates:
            ax.fill_between(dates, subs, color=MPL_ICE, alpha=0.7)
            ax.plot(dates, subs, color=MPL_NAVY, linewidth=2.5)
            ax.set_ylabel("Subscribers")
            ax.set_title("Subscriber Growth", color=MPL_NAVY, fontsize=14,
                         fontweight="bold", loc="left", pad=14)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: human_number(x)))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
            style_axes(ax)
            fig.autofmt_xdate()
            fig.tight_layout()
            fig.savefig(out_path, facecolor="white", bbox_inches="tight")
            plt.close(fig)
            return

    # Fallback: cumulative views proxy from recent uploads, anchored to current totals
    monthly = defaultdict(int)
    for v in videos:
        if not v.get("published_at"):
            continue
        d = datetime.fromisoformat(v["published_at"].replace("Z", "+00:00"))
        key = datetime(d.year, d.month, 1)
        monthly[key] += v["view_count"]
    months = sorted(monthly.keys())
    cumulative, running = [], 0
    for m in months:
        running += monthly[m]
        cumulative.append(running)
    if not months:
        plt.close(fig)
        return

    ax.fill_between(months, cumulative, color=MPL_ICE, alpha=0.7)
    ax.plot(months, cumulative, color=MPL_NAVY, linewidth=2.5)
    style_axes(ax)
    title = "Channel Growth — Cumulative Views (Recent Uploads)"
    ax.set_title(title, color=MPL_NAVY, fontsize=14, fontweight="bold",
                 loc="left", pad=14)
    ax.set_ylabel("Cumulative Views")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: human_number(x)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate()
    # Subtle disclaimer
    fig.text(0.99, 0.01,
             "Proxy: subscriber history requires YouTube Analytics API (OAuth). "
             "Supply subscriber_history.csv for the real curve.",
             fontsize=7, color=MPL_GREY, ha="right", va="bottom", style="italic")
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(out_path, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def chart_top_videos(videos: list, out_path: Path, n: int = 10):
    """Horizontal bar of top N videos by view count."""
    top = sorted(videos, key=lambda v: v["view_count"], reverse=True)[:n]
    if not top:
        return
    titles = [v["title"][:55] + ("…" if len(v["title"]) > 55 else "") for v in top]
    views = [v["view_count"] for v in top]

    # Reverse for top-down ranking
    titles = titles[::-1]
    views = views[::-1]

    fig, ax = plt.subplots(figsize=(11, 5.6), dpi=160)
    bars = ax.barh(titles, views, color=MPL_NAVY, edgecolor="white", height=0.7)
    # Highlight #1
    bars[-1].set_color(MPL_ACCENT)
    style_axes(ax)
    ax.spines["left"].set_visible(False)
    ax.tick_params(left=False)
    ax.set_title(f"Top {len(top)} Videos by Views", color=MPL_NAVY,
                 fontsize=14, fontweight="bold", loc="left", pad=14)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: human_number(x)))
    for bar, v in zip(bars, views):
        ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                human_number(v), va="center", color=MPL_NAVY, fontsize=9,
                fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path, facecolor="white", bbox_inches="tight")
    plt.close(fig)


# ── PPT helpers ──────────────────────────────────────────────────────────────

def set_bg(slide, color: RGBColor):
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, fill: RGBColor):
    shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = fill
    return shape


def add_text(slide, text: str, left, top, width, height,
             size=14, bold=False, color: RGBColor = None,
             align=PP_ALIGN.LEFT, font_name="Calibri"):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color or C_TEXT
    run.font.name = font_name


def blank_slide(prs: Presentation, bg=C_WHITE):
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    set_bg(slide, bg)
    for ph in list(slide.placeholders):
        ph._element.getparent().remove(ph._element)
    return slide


def page_title(slide, title: str, subtitle: str = ""):
    """Title + optional subtitle, no decorative line (per pptx skill best practice)."""
    add_text(slide, title, Inches(0.6), Inches(0.45), Inches(12), Inches(0.7),
             size=28, bold=True, color=C_NAVY, font_name="Cambria")
    if subtitle:
        add_text(slide, subtitle, Inches(0.6), Inches(1.05), Inches(12), Inches(0.4),
                 size=12, color=C_GREY)


def img(slide, path: Path, left, top, width, height):
    if path and Path(path).exists():
        slide.shapes.add_picture(str(path), left, top, width, height)


# ── Slide builders ───────────────────────────────────────────────────────────

def slide_cover(prs, channel: dict, run_date: str):
    s = blank_slide(prs, bg=C_NAVY)
    # Soft accent block bottom-right (visual motif: rounded ice-blue corner)
    add_rect(s, Inches(9.5), Inches(5.5), Inches(3.83), Inches(2.0), C_NAVY_DEEP)
    add_text(s, "CHANNEL PERFORMANCE REPORT",
             Inches(0.8), Inches(2.0), Inches(11), Inches(0.4),
             size=12, bold=True, color=C_ICE, font_name="Calibri")
    add_text(s, channel.get("title", "Untitled Channel"),
             Inches(0.8), Inches(2.5), Inches(11), Inches(1.4),
             size=44, bold=True, color=C_WHITE, font_name="Cambria")
    handle = channel.get("handle") or ""
    if handle:
        add_text(s, handle, Inches(0.8), Inches(3.95), Inches(11), Inches(0.5),
                 size=18, color=C_ICE, font_name="Calibri")
    add_text(s, f"Run date  ·  {run_date}",
             Inches(0.8), Inches(6.7), Inches(11), Inches(0.4),
             size=10, color=C_ICE)


def slide_snapshot(prs, channel: dict, videos: list):
    s = blank_slide(prs)
    page_title(s, "Channel Snapshot", "Current state at a glance")

    subs = channel.get("subscriber_count", 0)
    subs_label = "Hidden" if channel.get("subscribers_hidden") else human_number(subs)
    total_views = channel.get("total_views", 0)
    video_count = channel.get("video_count", 0)

    if videos:
        avg_eng = sum(v["engagement_rate"] for v in videos) / len(videos)
    else:
        avg_eng = 0
    eng_label = f"{avg_eng*100:.2f}%"

    cards = [
        ("Subscribers", subs_label),
        ("Total Views", human_number(total_views)),
        ("Videos Published", human_number(video_count)),
        ("Avg. Engagement", eng_label),
    ]
    cw = Inches(2.85)
    ch = Inches(1.7)
    gap = Inches(0.25)
    cy = Inches(2.0)
    for i, (label, val) in enumerate(cards):
        cx = Inches(0.6) + i * (cw + gap)
        add_rect(s, cx, cy, cw, ch, C_GREY_LIGHT)
        add_text(s, val, cx, cy + Inches(0.3), cw, Inches(0.7),
                 size=34, bold=True, color=C_NAVY,
                 align=PP_ALIGN.CENTER, font_name="Cambria")
        add_text(s, label, cx, cy + Inches(1.1), cw, Inches(0.4),
                 size=11, color=C_GREY, align=PP_ALIGN.CENTER)

    # Description block
    desc = channel.get("description", "")
    if desc:
        add_text(s, "About this channel",
                 Inches(0.6), Inches(4.2), Inches(12), Inches(0.4),
                 size=12, bold=True, color=C_NAVY)
        add_text(s, desc[:500],
                 Inches(0.6), Inches(4.6), Inches(12), Inches(2.3),
                 size=11, color=C_TEXT)


def slide_chart_full(prs, title: str, subtitle: str, chart_path: Path):
    s = blank_slide(prs)
    page_title(s, title, subtitle)
    img(s, chart_path, Inches(0.5), Inches(1.55), Inches(12.3), Inches(5.6))


def slide_engagement_insights(prs, videos: list):
    s = blank_slide(prs)
    page_title(s, "Engagement Insights", "Where the audience is most active")

    if not videos:
        add_text(s, "No video data available.", Inches(0.6), Inches(2),
                 Inches(12), Inches(0.5), size=14, color=C_GREY)
        return

    best = max(videos, key=lambda v: v["engagement_rate"])
    most_viewed = max(videos, key=lambda v: v["view_count"])
    shorts = [v for v in videos if v.get("is_short")]
    shorts_pct = (len(shorts) / len(videos)) * 100 if videos else 0

    rows = [
        ("Highest engagement", best["title"][:70],
         f"{best['engagement_rate']*100:.2f}% engagement"),
        ("Most viewed (recent)", most_viewed["title"][:70],
         f"{human_number(most_viewed['view_count'])} views"),
        ("Shorts share of recent uploads",
         f"{len(shorts)} of {len(videos)} recent uploads are Shorts",
         f"{shorts_pct:.0f}%"),
    ]
    ry = Inches(1.85)
    for label, headline, stat in rows:
        add_rect(s, Inches(0.6), ry, Inches(12.1), Inches(1.45), C_GREY_LIGHT)
        add_text(s, label, Inches(0.85), ry + Inches(0.18), Inches(11.8), Inches(0.35),
                 size=11, color=C_ACCENT, bold=True)
        add_text(s, headline, Inches(0.85), ry + Inches(0.55), Inches(8.2), Inches(0.5),
                 size=14, bold=True, color=C_TEXT, font_name="Cambria")
        add_text(s, stat, Inches(9.2), ry + Inches(0.45), Inches(3.4), Inches(0.6),
                 size=20, bold=True, color=C_NAVY,
                 align=PP_ALIGN.RIGHT, font_name="Cambria")
        ry += Inches(1.65)


def slide_takeaways(prs, channel: dict, videos: list):
    s = blank_slide(prs)
    page_title(s, "Key Takeaways", "Three observations grounded in the data")

    if not videos:
        return
    total_recent_views = sum(v["view_count"] for v in videos)
    avg_views = total_recent_views / len(videos)
    avg_eng = sum(v["engagement_rate"] for v in videos) / len(videos)
    top = sorted(videos, key=lambda v: v["view_count"], reverse=True)[:3]
    top_share = sum(v["view_count"] for v in top) / total_recent_views * 100 \
        if total_recent_views else 0

    items = [
        (
            "Audience scale",
            f"{human_number(channel.get('total_views', 0))} lifetime views across "
            f"{human_number(channel.get('video_count', 0))} videos — recent uploads "
            f"average {human_number(avg_views)} views each.",
        ),
        (
            "Engagement quality",
            f"Average engagement rate of {avg_eng*100:.2f}% on the last "
            f"{len(videos)} uploads. Above 4% is strong; below 2% suggests "
            f"audience-content drift.",
        ),
        (
            "Concentration of attention",
            f"The top 3 recent videos drove {top_share:.0f}% of total recent views — "
            f"a useful signal for which formats to double down on.",
        ),
    ]
    iy = Inches(1.85)
    for i, (head, body) in enumerate(items, 1):
        add_rect(s, Inches(0.6), iy, Inches(0.7), Inches(1.4), C_NAVY)
        add_text(s, str(i), Inches(0.6), iy + Inches(0.32),
                 Inches(0.7), Inches(0.7),
                 size=24, bold=True, color=C_WHITE,
                 align=PP_ALIGN.CENTER, font_name="Cambria")
        add_text(s, head, Inches(1.5), iy + Inches(0.1), Inches(11), Inches(0.45),
                 size=14, bold=True, color=C_NAVY, font_name="Cambria")
        add_text(s, body, Inches(1.5), iy + Inches(0.55), Inches(11), Inches(0.85),
                 size=11, color=C_TEXT)
        iy += Inches(1.6)


def slide_closing(prs, run_date: str):
    s = blank_slide(prs, bg=C_NAVY)
    add_text(s, "Thank you",
             Inches(0.8), Inches(2.6), Inches(12), Inches(1.2),
             size=54, bold=True, color=C_WHITE, font_name="Cambria")
    add_text(s, "Questions, comments, or follow-ups welcome.",
             Inches(0.8), Inches(4.0), Inches(12), Inches(0.5),
             size=16, color=C_ICE)
    add_text(s, f"Data sourced from YouTube Data API v3  ·  Generated {run_date}",
             Inches(0.8), Inches(6.7), Inches(12), Inches(0.4),
             size=10, color=C_ICE)


# ── Main ─────────────────────────────────────────────────────────────────────

def resolve_channel_id(youtube_data: dict) -> str:
    return youtube_data["channel"]["id"]


def main():
    parser = argparse.ArgumentParser(description="Generate a corporate PPT for one YouTube channel.")
    parser.add_argument("--channel", required=True,
                        help="Channel ID, @handle, or slug (must match the JSON already fetched)")
    parser.add_argument("--history", default=None,
                        help="Optional path to subscriber_history.csv (date,subscribers)")
    args = parser.parse_args()

    # Find the JSON file — try to map @handle/slug back to a fetched ID
    identifier = args.channel.strip()
    if identifier.startswith("UC") and len(identifier) >= 20:
        json_path = TMP_DIR / f"channel_{identifier}.json"
    else:
        # Search for any channel_*.json whose handle matches
        json_path = None
        wanted = identifier.lstrip("@").lower()
        for p in TMP_DIR.glob("channel_*.json"):
            try:
                with open(p, encoding="utf-8") as f:
                    rec = json.load(f)
                handle = rec["channel"].get("handle", "").lstrip("@").lower()
                title = rec["channel"].get("title", "").lower()
                if wanted in (handle, title):
                    json_path = p
                    break
            except Exception:
                continue

    if not json_path or not json_path.exists():
        print(f"ERROR: No channel JSON found for {args.channel}.")
        print("Run first:  python tools/fetch_channel_data.py --channel "
              f"\"{args.channel}\"")
        sys.exit(1)

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    channel = data["channel"]
    videos = data["videos"]
    channel_id = channel["id"]
    run_date = datetime.utcnow().strftime("%Y-%m-%d")

    # Charts dir
    charts_dir = TMP_DIR / f"channel_{channel_id}_charts"
    charts_dir.mkdir(exist_ok=True)
    chart_views = charts_dir / "views_over_time.png"
    chart_growth = charts_dir / "channel_growth.png"
    chart_top = charts_dir / "top_videos.png"

    print("Generating charts...")
    chart_views_over_time(videos, chart_views)
    history_path = Path(args.history) if args.history else None
    chart_growth_area(videos, channel, history_path, chart_growth)
    chart_top_videos(videos, chart_top, n=10)

    print("Building slide deck...")
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    slide_cover(prs, channel, run_date);                            print("  [1/8] Cover")
    slide_snapshot(prs, channel, videos);                           print("  [2/8] Snapshot")
    slide_chart_full(prs, "Views Over Time",
                     "Monthly view aggregate from recent uploads",
                     chart_views);                                  print("  [3/8] Views over time")
    growth_subtitle = ("Subscriber growth" if history_path and history_path.exists()
                       else "Cumulative views (subscriber history requires OAuth)")
    slide_chart_full(prs, "Channel Growth", growth_subtitle,
                     chart_growth);                                 print("  [4/8] Growth")
    slide_chart_full(prs, "Top Videos Ranking",
                     "Top 10 recent uploads by total view count",
                     chart_top);                                    print("  [5/8] Top videos")
    slide_engagement_insights(prs, videos);                         print("  [6/8] Engagement insights")
    slide_takeaways(prs, channel, videos);                          print("  [7/8] Key takeaways")
    slide_closing(prs, run_date);                                   print("  [8/8] Closing")

    out_path = TMP_DIR / f"channel_{channel_id}_{run_date}.pptx"
    prs.save(str(out_path))
    print(f"\n[OK] Slide deck saved -> {out_path}")


if __name__ == "__main__":
    main()
