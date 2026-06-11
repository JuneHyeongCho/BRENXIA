"""
Script to read the actual PMS template spreadsheet structure.
Reads all tab names, headers, and cell content from the template.
"""
import os
import json
import logging
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TEMPLATE_SPREADSHEET_ID = "1nnv1bV5bUfe-fjdJh8OWPQYdob0HBhttRgCDNjwHmPA"
CREDENTIALS_PATH = "config/credentials.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def main():
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH, scopes=SCOPES
    )
    sheets_service = build("sheets", "v4", credentials=credentials)

    # 1. Get all sheet (tab) metadata
    spreadsheet = sheets_service.spreadsheets().get(
        spreadsheetId=TEMPLATE_SPREADSHEET_ID,
        includeGridData=False,
    ).execute()

    sheets = spreadsheet.get("sheets", [])
    logger.info(f"Total tabs found: {len(sheets)}")

    result = {}

    for sheet in sheets:
        props = sheet["properties"]
        title = props["title"]
        sheet_id = props["sheetId"]
        row_count = props.get("gridProperties", {}).get("rowCount", 0)
        col_count = props.get("gridProperties", {}).get("columnCount", 0)
        logger.info(f"  Tab: '{title}' (sheetId={sheet_id}, rows={row_count}, cols={col_count})")

        # 2. Read first 60 rows of each tab to capture structure
        try:
            range_name = f"'{title}'!A1:Z60"
            data = sheets_service.spreadsheets().values().get(
                spreadsheetId=TEMPLATE_SPREADSHEET_ID,
                range=range_name,
                valueRenderOption="FORMATTED_VALUE",
            ).execute()
            values = data.get("values", [])
        except Exception as e:
            logger.warning(f"    Could not read '{title}': {e}")
            values = []

        result[title] = {
            "sheet_id": sheet_id,
            "row_count": row_count,
            "col_count": col_count,
            "data_rows": len(values),
            "content": values,
        }

        # Print first 30 rows for visibility
        for i, row in enumerate(values[:30], start=1):
            logger.info(f"    Row {i:2d}: {row}")

        if len(values) > 30:
            logger.info(f"    ... ({len(values) - 30} more rows)")

    # Save full result to JSON for reference
    output_path = "scripts/template_structure.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info(f"\nFull structure saved to: {output_path}")

    # Print tab order summary
    logger.info("\n=== TAB ORDER SUMMARY ===")
    for i, title in enumerate(result.keys(), 1):
        logger.info(f"  {i}. {title}")


if __name__ == "__main__":
    main()
