import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

def main():
    credentials_path = "config/credentials.json"
    shared_drive_id = "0AC60uqyzGV3aUk9PVA"
    
    if not os.path.exists(credentials_path):
        print(f"Credentials not found")
        return
        
    scopes = ['https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=scopes
    )
    
    drive_service = build('drive', 'v3', credentials=credentials)
    
    print("Listing files in Shared Drive:", shared_drive_id)
    try:
        list_args = {
            'q': "trashed = false",
            'spaces': 'drive',
            'fields': 'files(id, name, mimeType)',
            'supportsAllDrives': True,
            'includeItemsFromAllDrives': True,
            'corpora': 'drive',
            'driveId': shared_drive_id
        }
        results = drive_service.files().list(**list_args).execute()
        files = results.get("files", [])
        print(f"Found {len(files)} files:")
        for f in files:
            print(f"- Name: {f.get('name')}, ID: {f.get('id')}, MimeType: {f.get('mimeType')}")
    except Exception as e:
        print("Error listing files:", e)

if __name__ == "__main__":
    main()
