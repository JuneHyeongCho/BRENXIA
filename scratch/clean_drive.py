import os
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

def main():
    credentials_path = "config/credentials.json"
    if not os.path.exists(credentials_path):
        print(f"Credentials not found at {credentials_path}")
        return

    scopes = ['https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=scopes
    )
    drive_service = build('drive', 'v3', credentials=credentials)

    # Specific IDs created in the test
    target_ids = [
        "1vUMrL2FEdWTfPtcB40liT2k97K92nXrC",  # Project folder
        "1SqUr_pjtlZIM7EQ8f6FkDKpvlB5T7GnBRLQPD1Z21z0"  # PMS Spreadsheet
    ]

    for file_id in target_ids:
        print(f"Deleting item ID {file_id}...")
        try:
            drive_service.files().delete(
                fileId=file_id,
                supportsAllDrives=True
            ).execute()
            print("-> Successfully deleted.")
        except Exception as err:
            print(f"-> Failed: {err}")

if __name__ == "__main__":
    main()
