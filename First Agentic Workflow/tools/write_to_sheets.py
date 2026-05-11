"""
Write branded competitor analysis results to Google Sheets.
Usage: python write_to_sheets.py --run-date YYYY-MM-DD --data-dir .tmp/
Requires: GOOGLE_SHEETS_ID and GOOGLE_CREDENTIALS_JSON in .env
"""

import argparse
import json
import os
from pathlib import Path

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# AIS Brand colors (hex without #, as gspread uses this format)
BRAND = {
    "bg_surface": {"red": 0.051, "green": 0.149, "blue": 0.149},   # #0D2626
    "accent":     {"red": 0.0,   "green": 0.788, "blue": 0.627},   # #00C9A0
    "danger":     {"red": 0.878, "green": 0.333, "blue": 0.333},   # #E05555
    "white":      {"red": 1.0,   "green": 1.0,   "blue": 1.0},
    "muted":      {"red": 0.627, "green": 0.690,  "blue": 0.690},  # #A0B0B0
    "bg_primary": {"red": 0.102, "green": 0.118, "blue": 0.133},   # #1A1E22
}

SNAPSHOT_HEADERS = [
    "Competitor", "Website", "Last Updated", "Messaging Summary",
    "Pricing Tier", "Pricing Notes", "Review Sentiment", "Avg Rating",
    "Top Review Theme", "Active Job Count", "Key Hiring Areas",
    "Threat Level", "Threat Rationale", "Notable Changes", "Signals Available",
]

HISTORY_HEADERS = ["Run Date"] + SNAPSHOT_HEADERS


def rgb(color_key: str) -> dict:
    c = BRAND[color_key]
    return {"red": c["red"], "green": c["green"], "blue": c["blue"]}


def get_client() -> gspread.Client:
    creds_path = os.environ.get("GOOGLE_CREDENTIALS_JSON", "./credentials/google_service_account.json")
    creds_path = (BASE_DIR / creds_path).resolve()
    creds = Credentials.from_service_account_file(str(creds_path), scopes=SCOPES)
    return gspread.authorize(creds)


def get_or_create_sheet(spreadsheet: gspread.Spreadsheet, title: str) -> gspread.Worksheet:
    try:
        return spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=title, rows=500, cols=20)


def analysis_to_row(analysis: dict, run_date: str = None) -> list:
    hiring = ", ".join(analysis.get("key_hiring_areas") or [])
    signals = ", ".join(analysis.get("signals_available") or [])
    row = [
        analysis.get("competitor_name", ""),
        analysis.get("website_url", ""),
        run_date or analysis.get("run_date", ""),
        analysis.get("messaging_summary", ""),
        analysis.get("pricing_tier", ""),
        analysis.get("pricing_notes", ""),
        analysis.get("review_sentiment", ""),
        analysis.get("avg_rating", ""),
        analysis.get("top_review_theme", ""),
        analysis.get("active_job_count", ""),
        hiring,
        analysis.get("threat_level", ""),
        analysis.get("threat_rationale", ""),
        analysis.get("notable_changes", ""),
        signals,
    ]
    return row


def apply_header_format(sheet: gspread.Worksheet, spreadsheet: gspread.Spreadsheet, num_cols: int):
    """Apply AIS brand formatting to the header row."""
    sheet_id = sheet.id
    requests = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": num_cols,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": rgb("bg_surface"),
                        "textFormat": {
                            "foregroundColor": rgb("white"),
                            "bold": True,
                            "fontSize": 10,
                        },
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        },
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {"frozenRowCount": 1},
                },
                "fields": "gridProperties.frozenRowCount",
            }
        },
    ]
    spreadsheet.batch_update({"requests": requests})


def color_threat_cells(
    sheet: gspread.Worksheet,
    spreadsheet: gspread.Spreadsheet,
    analyses: list[dict],
    threat_col_index: int,
    start_row: int,
):
    """Color threat level cells: red for 4-5, green for 1-2."""
    requests = []
    for i, analysis in enumerate(analyses):
        level = analysis.get("threat_level")
        if not level:
            continue
        try:
            level = int(level)
        except (ValueError, TypeError):
            continue

        color = rgb("danger") if level >= 4 else (rgb("accent") if level <= 2 else None)
        if not color:
            continue

        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": start_row + i,
                    "endRowIndex": start_row + i + 1,
                    "startColumnIndex": threat_col_index,
                    "endColumnIndex": threat_col_index + 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": color,
                        "textFormat": {"bold": True},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        })

    if requests:
        spreadsheet.batch_update({"requests": requests})


def update_snapshot_tab(
    spreadsheet: gspread.Spreadsheet,
    analyses: list[dict],
    run_date: str,
):
    sheet = get_or_create_sheet(spreadsheet, "Weekly Snapshot")
    rows = [SNAPSHOT_HEADERS] + [analysis_to_row(a, run_date) for a in analyses]
    sheet.clear()
    sheet.update(rows, "A1")
    apply_header_format(sheet, spreadsheet, len(SNAPSHOT_HEADERS))
    threat_col = SNAPSHOT_HEADERS.index("Threat Level")
    color_threat_cells(sheet, spreadsheet, analyses, threat_col, start_row=1)
    print(f"  [OK] Weekly Snapshot updated ({len(analyses)} competitors)")


def update_history_tab(
    spreadsheet: gspread.Spreadsheet,
    analyses: list[dict],
    run_date: str,
):
    sheet = get_or_create_sheet(spreadsheet, "History")
    all_values = sheet.get_all_values()

    if not all_values or all_values[0] != HISTORY_HEADERS:
        sheet.insert_row(HISTORY_HEADERS, 1)
        apply_header_format(sheet, spreadsheet, len(HISTORY_HEADERS))

    new_rows = [[run_date] + analysis_to_row(a, run_date) for a in analyses]
    sheet.append_rows(new_rows, value_input_option="USER_ENTERED")
    print(f"  [OK] History tab: appended {len(new_rows)} rows")


def update_hiring_tab(
    spreadsheet: gspread.Spreadsheet,
    analyses: list[dict],
    run_date: str,
):
    HIRING_THRESHOLD = 3
    headers = ["Run Date", "Competitor", "Active Job Count", "Key Hiring Areas", "Interpretation"]
    notable = [
        a for a in analyses
        if a.get("active_job_count") and int(a.get("active_job_count", 0) or 0) >= HIRING_THRESHOLD
    ]
    if not notable:
        return

    sheet = get_or_create_sheet(spreadsheet, "Hiring Signals")
    all_values = sheet.get_all_values()
    if not all_values or all_values[0] != headers:
        sheet.insert_row(headers, 1)
        apply_header_format(sheet, spreadsheet, len(headers))

    rows = []
    for a in notable:
        hiring = ", ".join(a.get("key_hiring_areas") or [])
        interpretation = (
            f"Hiring surge in {hiring} may signal product expansion or GTM push."
            if hiring else "Significant hiring activity detected."
        )
        rows.append([run_date, a.get("competitor_name", ""), a.get("active_job_count", ""), hiring, interpretation])

    sheet.append_rows(rows, value_input_option="USER_ENTERED")
    print(f"  [OK] Hiring Signals: flagged {len(notable)} competitors")


def update_summary_tab(
    spreadsheet: gspread.Spreadsheet,
    analyses: list[dict],
    run_date: str,
):
    sheet = get_or_create_sheet(spreadsheet, "Summary")
    sheet.clear()

    high_threat = [a for a in analyses if int(a.get("threat_level", 0) or 0) >= 4]
    notable_changes = [a for a in analyses if a.get("notable_changes") and "first analysis" not in str(a.get("notable_changes", "")).lower()]

    rows = [
        ["AIS — Competitor Intelligence Report"],
        [""],
        ["Last Run Date", run_date],
        ["Total Competitors Tracked", len(analyses)],
        ["High Threat (Level 4-5)", len(high_threat)],
        ["Competitors with Notable Changes", len(notable_changes)],
        [""],
        ["High Threat Competitors"],
    ]
    for a in high_threat:
        rows.append([a.get("competitor_name", ""), f"Level {a.get('threat_level')}", a.get("threat_rationale", "")])

    rows += [[""], ["Analyst Notes (fill in manually)"], [""]]

    sheet.update(rows, "A1")

    # Brand the title row
    spreadsheet.batch_update({"requests": [
        {
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 3},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": rgb("bg_surface"),
                        "textFormat": {"foregroundColor": rgb("accent"), "bold": True, "fontSize": 14},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        }
    ]})
    print(f"  [OK] Summary tab updated")


def load_analyses(data_dir: str) -> list[dict]:
    analyses = []
    for path in Path(data_dir).glob("*_analysis.json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "parse_error" not in data:
                analyses.append(data)
    return analyses


def main():
    parser = argparse.ArgumentParser(description="Write AIS competitor analysis to Google Sheets")
    parser.add_argument("--run-date", required=True, help="Run date (YYYY-MM-DD)")
    parser.add_argument("--data-dir", default=".tmp", help="Directory containing *_analysis.json files")
    args = parser.parse_args()

    sheets_id = os.environ.get("GOOGLE_SHEETS_ID")
    if not sheets_id:
        print("ERROR: GOOGLE_SHEETS_ID not set in .env")
        return

    analyses = load_analyses(args.data_dir)
    if not analyses:
        print(f"No analysis files found in {args.data_dir}")
        return

    print(f"Writing {len(analyses)} competitor analyses to Google Sheets...")

    client = get_client()
    spreadsheet = client.open_by_key(sheets_id)

    update_snapshot_tab(spreadsheet, analyses, args.run_date)
    update_history_tab(spreadsheet, analyses, args.run_date)
    update_hiring_tab(spreadsheet, analyses, args.run_date)
    update_summary_tab(spreadsheet, analyses, args.run_date)

    print(f"\n[OK] Google Sheet updated: {spreadsheet.url}")


if __name__ == "__main__":
    main()
