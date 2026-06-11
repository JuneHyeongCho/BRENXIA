"""
Read ACTUAL FORMULAS from the PMS template spreadsheet.
Uses FORMULA render option to see the real cell formulas, not computed values.
"""
import json
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TEMPLATE_ID = "1nnv1bV5bUfe-fjdJh8OWPQYdob0HBhttRgCDNjwHmPA"
CREDS_PATH = "config/credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

def read_sheet_formulas(service, sheet_title: str, rows: int = 65) -> list:
    """Read formulas from a given sheet tab."""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=TEMPLATE_ID,
            range=f"'{sheet_title}'!A1:P{rows}",
            valueRenderOption="FORMULA",
        ).execute()
        return result.get("values", [])
    except Exception as e:
        logger.warning(f"Could not read '{sheet_title}': {e}")
        return []


def main():
    creds = service_account.Credentials.from_service_account_file(
        CREDS_PATH, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=creds)

    # Get all tab names
    meta = service.spreadsheets().get(
        spreadsheetId=TEMPLATE_ID, includeGridData=False
    ).execute()
    tabs = [s["properties"]["title"] for s in meta["sheets"]]
    logger.info(f"Tabs: {tabs}")

    analysis = {}

    for tab in tabs:
        rows = read_sheet_formulas(service, tab, rows=65)
        analysis[tab] = rows

        print(f"\n{'='*70}")
        print(f"TAB: {tab}")
        print(f"{'='*70}")
        for i, row in enumerate(rows, start=1):
            # Only print rows that have formula-like content (contain '=')
            row_str = str(row)
            has_formula = any(
                isinstance(cell, str) and cell.startswith("=")
                for cell in row
            )
            if has_formula or (row and any(cell for cell in row)):
                print(f"  Row {i:2d}: {row}")

    # Save full formula dump
    with open("scripts/formula_analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    logger.info("\nSaved to scripts/formula_analysis.json")


if __name__ == "__main__":
    main()
