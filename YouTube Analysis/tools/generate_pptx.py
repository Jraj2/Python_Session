"""
Generate a branded 12-slide PowerPoint from YouTube niche analysis data.
Usage: python tools/generate_pptx.py
Output: .tmp/youtube_analysis_YYYY-MM-DD.pptx
"""

import json
from datetime import datetime
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

BASE_DIR = Path(__file__).parent.parent
TMP_DIR = BASE_DIR / ".tmp"
CHARTS_DIR = TMP_DIR / "charts"

# ── Brand palette ─────────────────────────────────────────────────────────────
C_BG    = RGBColor(0x1A, 0x1E, 0x22)
C_CARD  = RGBColor(0x1E, 0x26, 0x2E)
C_DARK3 = RGBColor(0x0D, 0x14, 0x18)
C_ACCENT = RGBColor(0x00, 0xC9, 0xA0)
C_BLUE   = RGBColor(0x4D, 0x96, 0xFF)
C_WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
C_GREY   = RGBColor(0xAA, 0xAA, 0xAA)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


# ── Low-level helpers ─────────────────────────────────────────────────────────

def set_bg(slide, color: RGBColor):
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, fill: RGBColor, line_color: RGBColor = None):
    shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line_color:
        shape.line.color.rgb = line_color
    else:
        shape.line.color.rgb = fill  # invisible border
    return shape


def add_text(slide, text: str, left, top, width, height,
             size=12, bold=False, color: RGBColor = None,
             align=PP_ALIGN.LEFT, wrap=True) -> None:
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color or C_WHITE
    run.font.name = "Segoe UI"


def add_slide(prs: Presentation) -> object:
    layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(layout)
    set_bg(slide, C_BG)
    for ph in slide.placeholders:
        ph._element.getparent().remove(ph._element)
    return slide


def header(slide, title: str, subtitle: str = ""):
    """Teal accent bar + page title."""
    add_rect(slide, Inches(0), Inches(0.52), SLIDE_W, Pt(3), C_ACCENT)
    add_text(slide, title,
             Inches(0.5), Inches(0.06), Inches(12), Inches(0.5),
             size=22, bold=True)
    if subtitle:
        add_text(slide, subtitle,
                 Inches(0.5), Inches(0.58), Inches(12), Inches(0.28),
                 size=10, color=C_ACCENT)


def img(slide, path: str, left, top, width, height):
    if path and Path(path).exists():
        slide.shapes.add_picture(str(path), left, top, width, height)


def chart_path(name: str) -> str:
    return str(CHARTS_DIR / name)


# ── Individual slide builders ─────────────────────────────────────────────────

def slide_title(prs, run_date: str):
    s = add_slide(prs)
    # Left accent stripe
    add_rect(s, Inches(0), Inches(0), Inches(0.4), SLIDE_H, C_ACCENT)
    # Gradient-style dark overlay on right
    add_rect(s, Inches(0.4), Inches(0), Inches(12.93), SLIDE_H, C_BG)
    # Titles
    add_text(s, "AI & Automation", Inches(0.8), Inches(1.6), Inches(11), Inches(1.0),
             size=46, bold=True)
    add_text(s, "YouTube Niche Analysis", Inches(0.8), Inches(2.65), Inches(11), Inches(0.8),
             size=30, color=C_ACCENT)
    add_text(s, f"Content Intelligence Report  ·  {run_date}",
             Inches(0.8), Inches(3.6), Inches(11), Inches(0.4),
             size=13, color=C_GREY)
    # Divider
    add_rect(s, Inches(0.8), Inches(4.1), Inches(3), Pt(2), C_ACCENT)
    add_text(s, "Powered by YouTube Data API v3  +  Claude AI",
             Inches(0.8), Inches(6.9), Inches(11), Inches(0.35),
             size=9, color=C_GREY)


def slide_exec_summary(prs, analysis: dict, n_channels: int, n_videos: int):
    s = add_slide(prs)
    header(s, "Executive Summary")

    summary = analysis.get("executive_summary", "Analysis complete.")
    add_text(s, summary,
             Inches(0.5), Inches(0.92), Inches(12.3), Inches(0.9),
             size=11, color=C_GREY)

    # Stat cards
    card_data = [
        ("Channels\nAnalyzed",  str(n_channels)),
        ("Videos\nAnalyzed",    str(n_videos)),
        ("Topic\nClusters",     str(len(analysis.get("topic_clusters", [])))),
        ("Content\nGaps Found", str(len(analysis.get("content_gaps", [])))),
    ]
    cw, ch = Inches(2.8), Inches(1.35)
    gap = Inches(0.3)
    cy = Inches(1.95)
    for i, (label, val) in enumerate(card_data):
        cx = Inches(0.5) + i * (cw + gap)
        add_rect(s, cx, cy, cw, ch, C_CARD)
        add_rect(s, cx, cy, cw, Pt(3), C_ACCENT)
        add_text(s, val, cx, cy + Inches(0.12), cw, Inches(0.7),
                 size=30, bold=True, color=C_ACCENT, align=PP_ALIGN.CENTER)
        add_text(s, label, cx, cy + Inches(0.78), cw, Inches(0.5),
                 size=9, color=C_GREY, align=PP_ALIGN.CENTER)

    # Top recs preview
    add_text(s, "Top Content Opportunities",
             Inches(0.5), Inches(3.45), Inches(12), Inches(0.35),
             size=12, bold=True, color=C_ACCENT)
    recs = analysis.get("recommendations", [])
    for i, rec in enumerate(recs[:3]):
        ry = Inches(3.85) + i * Inches(1.05)
        add_rect(s, Inches(0.5), ry, Inches(12.3), Inches(0.95), C_CARD)
        add_rect(s, Inches(0.5), ry, Pt(4), Inches(0.95), C_ACCENT)
        add_text(s, rec.get("action", ""), Inches(0.72), ry + Pt(5),
                 Inches(12), Inches(0.4), size=10, bold=True)
        add_text(s, rec.get("rationale", ""), Inches(0.72), ry + Inches(0.48),
                 Inches(12), Inches(0.38), size=9, color=C_GREY)


def slide_full_chart(prs, title: str, subtitle: str, chart_file: str):
    s = add_slide(prs)
    header(s, title, subtitle)
    img(s, chart_path(chart_file), Inches(0.3), Inches(0.8), Inches(12.7), Inches(6.35))


def slide_top_videos(prs, videos: list):
    s = add_slide(prs)
    header(s, "Top Performing Videos", "Most-viewed recent videos in the AI niche")
    img(s, chart_path("top_videos_views.png"), Inches(0.3), Inches(0.85), Inches(7.2), Inches(5.8))

    # Right panel: video list
    top = sorted(videos, key=lambda v: v["view_count"], reverse=True)[:8]
    add_text(s, "Title", Inches(7.7), Inches(0.88), Inches(3.7), Inches(0.28),
             size=9, bold=True, color=C_ACCENT)
    add_text(s, "Views", Inches(11.5), Inches(0.88), Inches(1.5), Inches(0.28),
             size=9, bold=True, color=C_ACCENT)
    add_rect(s, Inches(7.6), Inches(1.18), Inches(5.4), Pt(1), C_ACCENT)

    for i, v in enumerate(top):
        vy = Inches(1.22) + i * Inches(0.77)
        add_rect(s, Inches(7.6), vy, Inches(5.4), Inches(0.7), C_CARD)
        t = v["title"][:44] + "…" if len(v["title"]) > 44 else v["title"]
        add_text(s, t, Inches(7.7), vy + Inches(0.04), Inches(3.6), Inches(0.38), size=8)
        add_text(s, v["channel_title"][:26], Inches(7.7), vy + Inches(0.4),
                 Inches(3.6), Inches(0.25), size=7, color=C_GREY)
        vv = v["view_count"]
        vs = f"{vv/1_000_000:.1f}M" if vv >= 1_000_000 else f"{vv//1000}K"
        add_text(s, vs, Inches(11.5), vy + Inches(0.15), Inches(1.4), Inches(0.4),
                 size=10, bold=True, color=C_ACCENT)


def slide_title_patterns(prs, analysis: dict):
    s = add_slide(prs)
    header(s, "Title Patterns & Trending Keywords", "Formats that consistently drive clicks")

    patterns = analysis.get("title_patterns", [])
    keywords = analysis.get("trending_keywords", [])

    # Left: patterns
    add_text(s, "High-Performing Title Formulas",
             Inches(0.5), Inches(0.88), Inches(7.5), Inches(0.35),
             size=11, bold=True, color=C_ACCENT)
    for i, p in enumerate(patterns[:4]):
        py = Inches(1.28) + i * Inches(1.42)
        add_rect(s, Inches(0.5), py, Inches(7.5), Inches(1.3), C_CARD)
        add_rect(s, Inches(0.5), py, Pt(4), Inches(1.3), C_ACCENT)
        add_text(s, p.get("pattern", ""), Inches(0.68), py + Inches(0.06),
                 Inches(7.2), Inches(0.4), size=10, bold=True)
        add_text(s, p.get("why_it_works", ""), Inches(0.68), py + Inches(0.5),
                 Inches(7.2), Inches(0.32), size=9, color=C_GREY)
        add_text(s, f"» {p.get('example', '')}", Inches(0.68), py + Inches(0.86),
                 Inches(7.2), Inches(0.38), size=8, color=C_ACCENT)

    # Right: keyword badges
    add_text(s, "Trending Keywords",
             Inches(8.3), Inches(0.88), Inches(4.6), Inches(0.35),
             size=11, bold=True, color=C_ACCENT)
    for i, kw in enumerate(keywords[:10]):
        ky = Inches(1.28) + i * Inches(0.6)
        add_rect(s, Inches(8.3), ky, Inches(4.6), Inches(0.5), C_CARD)
        add_rect(s, Inches(8.3), ky, Pt(4), Inches(0.5), C_BLUE)
        add_text(s, kw, Inches(8.48), ky + Inches(0.07),
                 Inches(4.4), Inches(0.38), size=10)


def slide_content_gaps(prs, analysis: dict):
    s = add_slide(prs)
    header(s, "Content Gaps & Opportunities", "Under-served topics with high audience demand")

    gaps = analysis.get("content_gaps", [])
    per_col = max(1, (len(gaps) + 1) // 2)
    for i, gap in enumerate(gaps):
        col = i // per_col
        row = i % per_col
        gx = Inches(0.5) + col * Inches(6.5)
        gy = Inches(0.92) + row * Inches(1.12)
        add_rect(s, gx, gy, Inches(6.2), Inches(1.0), C_CARD)
        add_rect(s, gx, gy, Pt(4), Inches(1.0), C_ACCENT)
        add_text(s, gap.get("gap", ""), gx + Inches(0.18), gy + Inches(0.06),
                 Inches(5.9), Inches(0.42), size=10, bold=True)
        add_text(s, gap.get("opportunity", ""), gx + Inches(0.18), gy + Inches(0.52),
                 Inches(5.9), Inches(0.4), size=9, color=C_GREY)


def slide_recommendations(prs, analysis: dict):
    s = add_slide(prs)
    header(s, "Content Strategy Recommendations", "Data-driven actions to grow your AI channel")

    recs = analysis.get("recommendations", [])
    for i, rec in enumerate(recs[:5]):
        ry = Inches(0.9) + i * Inches(1.22)
        add_rect(s, Inches(0.4), ry, Inches(12.5), Inches(1.1), C_CARD)
        # Number badge
        add_rect(s, Inches(0.4), ry, Inches(0.65), Inches(1.1), C_ACCENT)
        add_text(s, str(i + 1), Inches(0.4), ry + Inches(0.22),
                 Inches(0.65), Inches(0.65), size=20, bold=True,
                 color=C_BG, align=PP_ALIGN.CENTER)
        add_text(s, rec.get("action", ""), Inches(1.15), ry + Inches(0.06),
                 Inches(11.5), Inches(0.45), size=11, bold=True)
        add_text(s, rec.get("rationale", ""), Inches(1.15), ry + Inches(0.57),
                 Inches(11.5), Inches(0.42), size=9, color=C_GREY)


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

    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    run_date = analysis.get("run_date", datetime.utcnow().strftime("%Y-%m-%d"))

    print("Building slide deck...")
    slide_title(prs, run_date)
    print("  [1/12] Title")

    slide_exec_summary(prs, analysis, len(channels), len(videos))
    print("  [2/12] Executive Summary")

    slide_full_chart(prs, "Top Channels — Subscriber Count",
                     "Largest AI/automation creators by audience size",
                     "top_channels_subscribers.png")
    print("  [3/12] Top Channels (Subscribers)")

    slide_full_chart(prs, "Top Channels — Engagement Rate",
                     "Which channels drive the most likes & comments relative to views",
                     "top_channels_engagement.png")
    print("  [4/12] Top Channels (Engagement)")

    slide_top_videos(prs, videos)
    print("  [5/12] Top Performing Videos")

    slide_full_chart(prs, "Content Topic Landscape",
                     "How AI content breaks down across sub-topics in the niche",
                     "topic_distribution.png")
    print("  [6/12] Topic Distribution")

    slide_full_chart(prs, "Engagement Rate by Topic",
                     "Which content categories drive the most audience interaction",
                     "engagement_by_topic.png")
    print("  [7/12] Engagement by Topic")

    slide_full_chart(prs, "What Drives Views — Video Length Analysis",
                     "Relationship between video length and view count (color = engagement rate)",
                     "video_length_vs_views.png")
    print("  [8/12] Video Length vs Views")

    slide_full_chart(prs, "Upload Velocity in the AI Niche",
                     "Videos published per week over the last 12 weeks",
                     "upload_frequency.png")
    print("  [9/12] Upload Frequency")

    slide_title_patterns(prs, analysis)
    print(" [10/12] Title Patterns & Keywords")

    slide_content_gaps(prs, analysis)
    print(" [11/12] Content Gaps")

    slide_recommendations(prs, analysis)
    print(" [12/12] Strategy Recommendations")

    out_path = TMP_DIR / f"youtube_analysis_{run_date}.pptx"
    prs.save(str(out_path))
    print(f"\n[OK] Slide deck saved -> {out_path}")
    print("Open in PowerPoint, or upload to Google Drive → Google Slides for sharing.")


if __name__ == "__main__":
    main()
