import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

def main():
    credentials_path = "config/credentials.json"
    shared_drive_id = "0AC60uqyzGV3aUk9PVA"
    
    if not os.path.exists(credentials_path):
        print(f"Credentials not found at {credentials_path}")
        return
        
    scopes = ['https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=scopes
    )
    
    drive_service = build('drive', 'v3', credentials=credentials)
    
    print("Fetching permissions for Shared Drive:", shared_drive_id)
    try:
        results = drive_service.permissions().list(
            fileId=shared_drive_id,
            supportsAllDrives=True,
            fields="permissions(id, displayName, emailAddress, role, type)"
        ).execute()
        
        permissions = results.get("permissions", [])
        print(f"Found {len(permissions)} members/permissions:")
        for p in permissions:
            print(f"- Name: {p.get('displayName')}, Email: {p.get('emailAddress')}, Role: {p.get('role')}, Type: {p.get('type')}")
    except Exception as e:
        print("Error fetching permissions:", e)

if __name__ == "__main__":
    main()
