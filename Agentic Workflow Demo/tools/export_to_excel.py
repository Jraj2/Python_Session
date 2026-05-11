"""
export_to_excel.py

Reads any JSON array file and exports a formatted Excel workbook.
Auto-detects columns from the data; optional schema presets for known datasets.

Usage:
    python tools/export_to_excel.py [--input PATH] [--output PATH] [--preset PRESET]

Presets:   jobs | eu_jobs | dentist_leads
           (auto-detected from filename if not specified)

Output features:
    - Frozen header row with bold + colored styling
    - Auto-sized columns (capped at 80 chars)
    - Clickable hyperlinks in any column ending in '_url' or 'url'
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

BASE_DIR = Path(__file__).parent.parent
TMP_DIR = BASE_DIR / ".tmp"

# ── Column schema presets ──────────────────────────────────────────────────
SCHEMAS = {
    "jobs": {
        "columns": ["title", "company", "location", "job_type", "category",
                    "salary", "experience", "date_posted", "url"],
        "headers": {
            "title": "Job Title", "company": "Company",
            "location": "Location / Timezone", "job_type": "Job Type",
            "category": "Category", "salary": "Salary",
            "experience": "Experience Required", "date_posted": "Date Posted",
            "url": "Listing URL",
        },
        "url_cols": ["url"],
        "header_color": "2E75B6",
        "default_output": f"dailyremote_jobs_{datetime.now().strftime('%Y%m%d')}.xlsx",
    },
    "eu_jobs": {
        "columns": ["title", "company", "location", "job_type", "category",
                    "source_category", "salary", "experience", "date_posted", "url"],
        "headers": {
            "title": "Job Title", "company": "Company",
            "location": "Location / Timezone", "job_type": "Job Type",
            "category": "Category", "source_category": "Source Category",
            "salary": "Salary", "experience": "Experience Required",
            "date_posted": "Date Posted", "url": "Listing URL",
        },
        "url_cols": ["url"],
        "header_color": "2E75B6",
        "default_output": f"eu_jobs_{datetime.now().strftime('%Y%m%d')}.xlsx",
    },
    "dentist_leads": {
        "columns": ["practice_name", "phone", "street_address", "city", "state",
                    "zip_code", "specialties", "website", "rating",
                    "review_count", "yp_url"],
        "headers": {
            "practice_name": "Practice Name",
            "phone":         "Phone Number",
            "street_address": "Street Address",
            "city":          "City",
            "state":         "State",
            "zip_code":      "ZIP Code",
            "specialties":   "Specialties",
            "website":       "Website",
            "rating":        "Rating",
            "review_count":  "Review Count",
            "yp_url":        "YellowPages URL",
        },
        "url_cols": ["website", "yp_url"],
        "header_color": "1F6B3A",  # green for leads
        "default_output": f"dentist_leads_{datetime.now().strftime('%Y%m%d')}.xlsx",
    },
}


def detect_preset(input_path: Path, data: list) -> str:
    """Guess preset from filename or data keys."""
    name = input_path.stem.lower()
    if "dentist" in name:
        return "dentist_leads"
    if "eu_jobs" in name:
        return "eu_jobs"
    if data and "practice_name" in data[0]:
        return "dentist_leads"
    if data and "source_category" in data[0]:
        return "eu_jobs"
    return "jobs"


def build_dataframe(data: list, schema: dict) -> pd.DataFrame:
    columns = [c for c in schema["columns"] if c in (data[0] if data else {})]
    # Fall back to all columns from data if schema cols don't match
    if not columns:
        columns = list(data[0].keys()) if data else []

    url_cols = set(schema.get("url_cols", []))
    rows = []
    for record in data:
        row = {}
        for col in columns:
            val = str(record.get(col, "") or "").strip()
            if col not in url_cols and val == "":
                val = "N/A"
            row[col] = val
        rows.append(row)

    df = pd.DataFrame(rows, columns=columns)
    headers = schema.get("headers", {})
    df.rename(columns={c: headers.get(c, c) for c in columns}, inplace=True)
    return df


def style_workbook(output_path: Path, schema: dict) -> None:
    wb = load_workbook(output_path)
    ws = wb.active

    color = schema.get("header_color", "2E75B6")
    header_font  = Font(bold=True, color="FFFFFF")
    header_fill  = PatternFill(fill_type="solid", fgColor=color)
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=False)

    for cell in ws[1]:
        cell.font  = header_font
        cell.fill  = header_fill
        cell.alignment = center_align

    ws.freeze_panes = "A2"

    # Auto-size columns
    for col_idx, col_cells in enumerate(ws.columns, start=1):
        max_len = max(
            (len(str(cell.value)) if cell.value else 0) for cell in col_cells
        )
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 4, 80)

    # Hyperlinks — any column whose key ends in 'url' or 'website'
    url_col_keys = set(schema.get("url_cols", []))
    headers_inv = {v: k for k, v in schema.get("headers", {}).items()}
    link_font = Font(color="0563C1", underline="single")

    for cell in ws[1]:
        orig_key = headers_inv.get(str(cell.value), "")
        if orig_key in url_col_keys or str(cell.value).lower() in {"website", "url"}:
            col_idx = cell.column
            for row in ws.iter_rows(min_row=2, min_col=col_idx, max_col=col_idx):
                c = row[0]
                if c.value and str(c.value).startswith("http"):
                    c.hyperlink = str(c.value)
                    c.font = link_font

    wb.save(output_path)


def main():
    parser = argparse.ArgumentParser(description="Export any JSON array to formatted Excel")
    parser.add_argument("--input",  type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--preset", choices=list(SCHEMAS.keys()), default=None)
    args = parser.parse_args()

    input_path = args.input or (TMP_DIR / "jobs_raw.json")

    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", flush=True)
        raise SystemExit(1)

    print(f"Loading data from {input_path}...")
    data = json.loads(input_path.read_text(encoding="utf-8"))
    print(f"  {len(data)} records loaded.")

    preset = args.preset or detect_preset(input_path, data)
    schema = SCHEMAS.get(preset, SCHEMAS["jobs"])
    print(f"  Using schema preset: {preset!r}")

    output_path = args.output or (TMP_DIR / schema["default_output"])

    df = build_dataframe(data, schema)

    TMP_DIR.mkdir(exist_ok=True)
    df.to_excel(output_path, index=False, engine="openpyxl")

    print("Applying formatting...")
    style_workbook(output_path, schema)

    print(f"\nDone. Excel file saved to:\n  {output_path.resolve()}")
    print(f"  Rows: {len(df)}  |  Columns: {len(df.columns)}")


if __name__ == "__main__":
    main()
