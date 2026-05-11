"""
Generates a Matplotlib chart PNG from a JSON chart spec. No display window needed.
Usage: python tools/create_infographic.py --spec '{"type":"bar","title":"...","labels":[...],"values":[...]}'
       python tools/create_infographic.py --spec-file chart_spec.json
Outputs PNG to .tmp/charts/ and prints the file path.
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # non-interactive backend — no display required
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = Path(__file__).parent.parent
CHARTS_DIR = ROOT / ".tmp" / "charts"


PALETTE = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]
BG_COLOR = "#F8FAFC"
TEXT_COLOR = "#1E293B"
GRID_COLOR = "#E2E8F0"


def style_axes(ax):
    ax.set_facecolor(BG_COLOR)
    ax.tick_params(colors=TEXT_COLOR, labelsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID_COLOR)
    ax.spines["bottom"].set_color(GRID_COLOR)
    ax.yaxis.grid(True, color=GRID_COLOR, linestyle="--", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def bar_chart(spec: dict, ax, fig):
    labels = spec["labels"]
    values = spec["values"]
    colors = PALETTE[: len(labels)]
    bars = ax.bar(labels, values, color=colors, width=0.55, zorder=3)
    ax.set_title(spec.get("title", ""), fontsize=15, fontweight="bold", color=TEXT_COLOR, pad=14)
    if spec.get("ylabel"):
        ax.set_ylabel(spec["ylabel"], fontsize=11, color=TEXT_COLOR)
    style_axes(ax)
    # Value labels on bars
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.01,
            f"{val:,}",
            ha="center", va="bottom", fontsize=10, color=TEXT_COLOR, fontweight="bold",
        )


def horizontal_bar_chart(spec: dict, ax, fig):
    labels = spec["labels"]
    values = spec["values"]
    colors = PALETTE[: len(labels)]
    bars = ax.barh(labels, values, color=colors, height=0.55, zorder=3)
    ax.set_title(spec.get("title", ""), fontsize=15, fontweight="bold", color=TEXT_COLOR, pad=14)
    if spec.get("xlabel"):
        ax.set_xlabel(spec["xlabel"], fontsize=11, color=TEXT_COLOR)
    ax.invert_yaxis()
    style_axes(ax)
    ax.yaxis.grid(False)
    ax.xaxis.grid(True, color=GRID_COLOR, linestyle="--", linewidth=0.8, zorder=0)
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_width() + max(values) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{val:,}",
            ha="left", va="center", fontsize=10, color=TEXT_COLOR, fontweight="bold",
        )


def line_chart(spec: dict, ax, fig):
    labels = spec["labels"]
    values = spec["values"]
    ax.plot(labels, values, color=PALETTE[0], linewidth=2.5, marker="o", markersize=7, zorder=3)
    ax.fill_between(labels, values, alpha=0.12, color=PALETTE[0])
    ax.set_title(spec.get("title", ""), fontsize=15, fontweight="bold", color=TEXT_COLOR, pad=14)
    if spec.get("ylabel"):
        ax.set_ylabel(spec["ylabel"], fontsize=11, color=TEXT_COLOR)
    style_axes(ax)


def pie_chart(spec: dict, ax, fig):
    labels = spec["labels"]
    values = spec["values"]
    colors = PALETTE[: len(labels)]
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=140,
        textprops={"color": TEXT_COLOR, "fontsize": 11},
        wedgeprops={"linewidth": 1.5, "edgecolor": "white"},
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")
    ax.set_title(spec.get("title", ""), fontsize=15, fontweight="bold", color=TEXT_COLOR, pad=14)


CHART_TYPES = {
    "bar": bar_chart,
    "horizontal_bar": horizontal_bar_chart,
    "line": line_chart,
    "pie": pie_chart,
}


def generate(spec: dict) -> Path:
    chart_type = spec.get("type", "bar")
    if chart_type not in CHART_TYPES:
        sys.exit(f"Unknown chart type '{chart_type}'. Choose from: {list(CHART_TYPES)}")

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor(BG_COLOR)

    CHART_TYPES[chart_type](spec, ax, fig)

    plt.tight_layout(pad=1.5)

    slug = spec.get("title", "chart").lower().replace(" ", "_")[:30]
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = CHARTS_DIR / f"{slug}_{ts}.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print(f"Chart saved -> {out_path}")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--spec", help="JSON chart spec as string")
    group.add_argument("--spec-file", help="Path to JSON chart spec file")
    args = parser.parse_args()

    if args.spec:
        spec_data = json.loads(args.spec)
    else:
        spec_data = json.loads(Path(args.spec_file).read_text())

    path = generate(spec_data)
    print(path)
