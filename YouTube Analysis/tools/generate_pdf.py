"""
Generate a branded 12-page PDF from YouTube niche analysis data.
Usage: python tools/generate_pdf.py
Output: .tmp/youtube_analysis_YYYY-MM-DD.pdf
Requires: pip install reportlab
"""

import io
import json
from datetime import datetime
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph

BASE_DIR   = Path(__file__).parent.parent
TMP_DIR    = BASE_DIR / ".tmp"
CHARTS_DIR = TMP_DIR / "charts"
LOGO_PATH  = BASE_DIR / "assets" / "AIS_logo.png"

PAGE_W = 13.33 * 72   # 959.76 pt
PAGE_H = 7.5  * 72    # 540.0 pt

C_BG     = "#1A1E22"
C_CARD   = "#1E262E"
C_ACCENT = "#00C9A0"
C_BLUE   = "#4D96FF"
C_WHITE  = "#FFFFFF"
C_GREY   = "#AAAAAA"

_ALIGN_MAP = {"left": TA_LEFT, "center": TA_CENTER, "right": TA_RIGHT}


# ── Image helpers ─────────────────────────────────────────────────────────────

def _flatten(path):
    """Open any PNG and return an RGB ImageReader (handles RGBA transparently)."""
    p = Path(path)
    if not p.exists():
        return None
    img = PILImage.open(p)
    if img.mode == "RGBA":
        bg = PILImage.new("RGB", img.size, (0x1A, 0x1E, 0x22))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


# ── Drawing primitives ────────────────────────────────────────────────────────
# All y_top values are measured from the TOP of the page (PPTX convention).
# Internally converted to ReportLab's bottom-left origin: rl_y = PAGE_H - y_top - h

def new_page(c):
    c.setFillColor(HexColor(C_BG))
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)


def draw_rect(c, x, y_top, w, h, fill):
    c.setFillColor(HexColor(fill))
    c.rect(x, PAGE_H - y_top - h, w, h, fill=1, stroke=0)


def draw_text(c, text, x, y_top, w, h, size=11, bold=False, color=C_WHITE, align="left"):
    style = ParagraphStyle(
        "t",
        fontName="Helvetica-Bold" if bold else "Helvetica",
        fontSize=size,
        textColor=HexColor(color),
        leading=size * 1.25,
        spaceBefore=0,
        spaceAfter=0,
        alignment=_ALIGN_MAP.get(align, TA_LEFT),
    )
    safe = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    p = Paragraph(safe, style)
    f = Frame(x, PAGE_H - y_top - h, w, h,
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, showBoundary=0)
    f.addFromList([p], c)


def draw_para(c, text, x, y_top, w, h, size=10, color=C_WHITE, bold=False, align="left"):
    """Word-wrapped multi-line text."""
    style = ParagraphStyle(
        "p",
        fontName="Helvetica-Bold" if bold else "Helvetica",
        fontSize=size,
        textColor=HexColor(color),
        leading=size * 1.35,
        spaceBefore=0,
        spaceAfter=0,
        alignment=_ALIGN_MAP.get(align, TA_LEFT),
        wordWrap="LTR",
    )
    safe = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    p = Paragraph(safe.replace("\n", "<br/>"), style)
    f = Frame(x, PAGE_H - y_top - h, w, h,
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, showBoundary=0)
    f.addFromList([p], c)


def draw_image(c, path, x, y_top, w, h):
    reader = _flatten(path)
    if reader is None:
        return
    c.drawImage(reader, x, PAGE_H - y_top - h, w, h, preserveAspectRatio=False)


def draw_logo(c, x, y_top, max_w, max_h):
    """Draw AIS logo maintaining aspect ratio within the max bounding box."""
    if not LOGO_PATH.exists():
        return
    img = PILImage.open(LOGO_PATH)
    orig_w, orig_h = img.size
    scale = min(max_w / orig_w, max_h / orig_h)
    w, h = orig_w * scale, orig_h * scale
    if img.mode == "RGBA":
        bg = PILImage.new("RGB", img.size, (0x1A, 0x1E, 0x22))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    c.drawImage(ImageReader(buf), x, PAGE_H - y_top - h, w, h, preserveAspectRatio=False)


def draw_header(c, title, subtitle=""):
    """Teal accent bar + page title + optional subtitle. Used on pages 2–12."""
    draw_rect(c, 0, 37.44, PAGE_W, 3, C_ACCENT)
    draw_text(c, title, 36, 4.32, 864, 36, size=22, bold=True)
    if subtitle:
        draw_text(c, subtitle, 36, 41.76, 864, 20.16, size=10, color=C_ACCENT)
    # Small AIS logo top-right, sitting just above the teal bar
    draw_logo(c, PAGE_W - 56, 2, 50, 34)


def draw_footer(c, page_num, total=12):
    draw_text(c, "Confidential — AIS Internal Use Only",
              36, 526, 500, 14, size=7, color=C_GREY)
    draw_text(c, f"Page {page_num} of {total}",
              PAGE_W - 90, 526, 80, 14, size=7, color=C_GREY, align="right")


def fmt(n):
    n = int(n or 0)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n // 1_000}K"
    return str(n)


def chart(name):
    return CHARTS_DIR / name


# ── Page builders ─────────────────────────────────────────────────────────────

def page_cover(c, run_date):
    new_page(c)
    # Left teal stripe
    draw_rect(c, 0, 0, 28.8, 540, C_ACCENT)
    draw_rect(c, 28.8, 0, PAGE_W - 28.8, 540, C_BG)
    # Titles
    draw_text(c, "AI & Automation",       57.6, 115.2, 792, 72,   size=46, bold=True)
    draw_text(c, "YouTube Niche Analysis", 57.6, 190.8, 792, 57.6, size=30, color=C_ACCENT)
    draw_text(c, f"Content Intelligence Report  ·  {run_date}",
              57.6, 259.2, 792, 28.8, size=13, color=C_GREY)
    draw_rect(c, 57.6, 295.2, 216, 2, C_ACCENT)
    draw_text(c, "Powered by YouTube Data API v3  +  Claude AI",
              57.6, 496.8, 792, 25.2, size=9, color=C_GREY)
    # AIS logo — prominent, top-right
    draw_logo(c, PAGE_W - 140, 14, 120, 115)


def page_exec_summary(c, analysis, n_channels, n_videos):
    new_page(c)
    draw_header(c, "Executive Summary")

    summary = analysis.get("executive_summary", "Analysis complete.")
    draw_para(c, summary, 36, 66.24, 885.6, 64.8, size=11, color=C_GREY)

    # 4 stat cards
    card_data = [
        ("Channels Analyzed",  str(n_channels)),
        ("Videos Analyzed",    str(n_videos)),
        ("Topic Clusters",     str(len(analysis.get("topic_clusters", [])))),
        ("Content Gaps Found", str(len(analysis.get("content_gaps", [])))),
    ]
    cw, ch, gap = 201.6, 97.2, 21.6
    cy = 140.4
    for i, (label, val) in enumerate(card_data):
        cx = 36 + i * (cw + gap)
        draw_rect(c, cx, cy,        cw, ch, C_CARD)
        draw_rect(c, cx, cy,        cw, 3,  C_ACCENT)
        draw_text(c, val,   cx, cy + 8.64,  cw, 50.4, size=30, bold=True, color=C_ACCENT, align="center")
        draw_text(c, label, cx, cy + 65,    cw, 30,   size=9,  color=C_GREY,   align="center")

    # Top recommendations preview
    draw_text(c, "Top Content Opportunities",
              36, 248.4, 864, 25.2, size=12, bold=True, color=C_ACCENT)
    recs = analysis.get("recommendations", [])
    for i, rec in enumerate(recs[:3]):
        ry = 277.2 + i * 75.6
        draw_rect(c, 36, ry, 885.6, 68.4, C_CARD)
        draw_rect(c, 36, ry, 4,     68.4, C_ACCENT)
        draw_text(c, rec.get("action", ""),
                  51.84, ry + 5, 828, 28.8, size=10, bold=True)
        draw_para(c, rec.get("rationale", ""),
                  51.84, ry + 36, 828, 27, size=9, color=C_GREY)

    draw_footer(c, 2)


def page_full_chart(c, title, subtitle, chart_file, page_num):
    new_page(c)
    draw_header(c, title, subtitle)
    draw_image(c, chart(chart_file), 21.6, 62, PAGE_W - 43.2, 450)
    draw_footer(c, page_num)


def page_top_videos(c, videos, page_num):
    new_page(c)
    draw_header(c, "Top Performing Videos", "Most-viewed recent videos in the AI niche")
    draw_image(c, chart("top_videos_views.png"), 21.6, 61.2, 518.4, 417.6)

    top = sorted(videos, key=lambda v: v.get("view_count", 0), reverse=True)[:8]
    draw_text(c, "Title",  554.4, 63.36, 266.4, 20.16, size=9, bold=True, color=C_ACCENT)
    draw_text(c, "Views",  828,   63.36, 108,   20.16, size=9, bold=True, color=C_ACCENT)
    draw_rect(c, 547.2, 85.0, 388.8, 1, C_ACCENT)

    for i, v in enumerate(top):
        vy = 87.84 + i * 55.44
        draw_rect(c, 547.2, vy, 388.8, 50.4, C_CARD)
        title_t = v["title"][:44] + "…" if len(v["title"]) > 44 else v["title"]
        draw_text(c, title_t,              554.4, vy + 2.88, 259.2, 27.36, size=8)
        draw_text(c, v["channel_title"][:26], 554.4, vy + 28.8, 259.2, 18, size=7, color=C_GREY)
        draw_text(c, fmt(v.get("view_count", 0)), 828, vy + 10.8, 100.8, 28.8,
                  size=10, bold=True, color=C_ACCENT)

    draw_footer(c, page_num)


def page_title_patterns(c, analysis, page_num):
    new_page(c)
    draw_header(c, "Title Patterns & Trending Keywords", "Formats that consistently drive clicks")

    patterns = analysis.get("title_patterns", [])
    keywords = analysis.get("trending_keywords", [])

    draw_text(c, "High-Performing Title Formulas",
              36, 63.36, 540, 25.2, size=11, bold=True, color=C_ACCENT)
    for i, p in enumerate(patterns[:4]):
        py = 92.16 + i * 102.24
        draw_rect(c, 36, py, 540, 93.6, C_CARD)
        draw_rect(c, 36, py, 4,   93.6, C_ACCENT)
        draw_text(c, p.get("pattern", ""),
                  48.96, py + 4.32, 518.4, 28.8, size=10, bold=True)
        draw_para(c, p.get("why_it_works", ""),
                  48.96, py + 36, 518.4, 23, size=9, color=C_GREY)
        draw_text(c, f"» {p.get('example', '')}",
                  48.96, py + 61.92, 518.4, 27.36, size=8, color=C_ACCENT)

    draw_text(c, "Trending Keywords",
              597.6, 63.36, 331.2, 25.2, size=11, bold=True, color=C_ACCENT)
    for i, kw in enumerate(keywords[:10]):
        ky = 92.16 + i * 43.2
        draw_rect(c, 597.6, ky, 331.2, 36, C_CARD)
        draw_rect(c, 597.6, ky, 4,     36, C_BLUE)
        draw_text(c, kw, 610.56, ky + 5, 316.8, 27, size=10)

    draw_footer(c, page_num)


def page_content_gaps(c, analysis, page_num):
    new_page(c)
    draw_header(c, "Content Gaps & Opportunities", "Under-served topics with high audience demand")

    gaps = analysis.get("content_gaps", [])
    per_col = max(1, (len(gaps) + 1) // 2)
    for i, gap in enumerate(gaps):
        col = i // per_col
        row = i % per_col
        gx = 36 + col * 468
        gy = 66.24 + row * 80.64
        draw_rect(c, gx, gy, 446.4, 72, C_CARD)
        draw_rect(c, gx, gy, 4,     72, C_ACCENT)
        draw_text(c, gap.get("gap", ""),
                  gx + 12.96, gy + 4.32, 424.8, 30, size=10, bold=True)
        draw_para(c, gap.get("opportunity", ""),
                  gx + 12.96, gy + 37, 424.8, 29, size=9, color=C_GREY)

    draw_footer(c, page_num)


def page_recommendations(c, analysis, page_num):
    new_page(c)
    draw_header(c, "Content Strategy Recommendations", "Data-driven actions to grow your AI channel")

    recs = analysis.get("recommendations", [])
    for i, rec in enumerate(recs[:5]):
        ry = 64.8 + i * 87.84
        draw_rect(c, 28.8, ry, 900,  79.2, C_CARD)
        draw_rect(c, 28.8, ry, 46.8, 79.2, C_ACCENT)
        draw_text(c, str(i + 1), 28.8, ry + 16, 46.8, 46, size=20, bold=True,
                  color=C_BG, align="center")
        draw_text(c, rec.get("action", ""),
                  82.8, ry + 4.32, 828, 32.4, size=11, bold=True)
        draw_para(c, rec.get("rationale", ""),
                  82.8, ry + 41, 828, 30, size=9, color=C_GREY)

    draw_footer(c, page_num)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    for fname in ["channels.json", "videos.json", "analysis.json"]:
        if not (TMP_DIR / fname).exists():
            print(f"ERROR: .tmp/{fname} not found. Run pipeline steps 1–4 first.")
            return

    channels = json.load(open(TMP_DIR / "channels.json", encoding="utf-8"))["channels"]
    videos   = json.load(open(TMP_DIR / "videos.json",   encoding="utf-8"))["videos"]
    analysis = json.load(open(TMP_DIR / "analysis.json", encoding="utf-8"))

    run_date = analysis.get("run_date", datetime.utcnow().strftime("%Y-%m-%d"))
    out_path = TMP_DIR / f"youtube_analysis_{run_date}.pdf"

    c = canvas.Canvas(str(out_path), pagesize=(PAGE_W, PAGE_H))
    c.setTitle("AI & Automation YouTube Niche Analysis")
    c.setAuthor("AIS — Powered by YouTube Data API v3 + Claude AI")

    print("Building PDF report...")

    page_cover(c, run_date);                                                              c.showPage(); print("  [1/12] Cover")
    page_exec_summary(c, analysis, len(channels), len(videos));                          c.showPage(); print("  [2/12] Executive Summary")
    page_full_chart(c, "Top Channels — Subscriber Count",
                    "Largest AI/automation creators by audience size",
                    "top_channels_subscribers.png", 3);                                  c.showPage(); print("  [3/12] Top Channels (Subscribers)")
    page_full_chart(c, "Top Channels — Engagement Rate",
                    "Which channels drive the most likes & comments relative to views",
                    "top_channels_engagement.png", 4);                                   c.showPage(); print("  [4/12] Top Channels (Engagement)")
    page_top_videos(c, videos, 5);                                                       c.showPage(); print("  [5/12] Top Performing Videos")
    page_full_chart(c, "Content Topic Landscape",
                    "How AI content breaks down across sub-topics in the niche",
                    "topic_distribution.png", 6);                                        c.showPage(); print("  [6/12] Topic Distribution")
    page_full_chart(c, "Engagement Rate by Topic",
                    "Which content categories drive the most audience interaction",
                    "engagement_by_topic.png", 7);                                       c.showPage(); print("  [7/12] Engagement by Topic")
    page_full_chart(c, "What Drives Views — Video Length Analysis",
                    "Relationship between video length and view count (color = engagement rate)",
                    "video_length_vs_views.png", 8);                                     c.showPage(); print("  [8/12] Video Length vs Views")
    page_full_chart(c, "Upload Velocity in the AI Niche",
                    "Videos published per week over the last 12 weeks",
                    "upload_frequency.png", 9);                                          c.showPage(); print("  [9/12] Upload Frequency")
    page_title_patterns(c, analysis, 10);                                                c.showPage(); print(" [10/12] Title Patterns & Keywords")
    page_content_gaps(c, analysis, 11);                                                  c.showPage(); print(" [11/12] Content Gaps")
    page_recommendations(c, analysis, 12);                                               c.showPage(); print(" [12/12] Strategy Recommendations")

    c.save()
    print(f"\n[OK] PDF saved -> {out_path}")


if __name__ == "__main__":
    main()
