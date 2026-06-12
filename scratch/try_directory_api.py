import os
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

def main():
    # Reconfigure stdout to use UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    credentials_path = "config/credentials.json"
    if not os.path.exists(credentials_path):
        print("Credentials not found")
        return
        
    scopes = ['https://www.googleapis.com/auth/admin.directory.user.readonly']
    
    try:
        credentials_sub2 = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=scopes,
            subject="brenxia@brenxia.com"
        )
        admin_service_sub2 = build('admin', 'directory_v1', credentials=credentials_sub2)
        results = admin_service_sub2.users().list(customer='my_customer', maxResults=50).execute()
        users = results.get('users', [])
        print(f"Success with subject brenxia@brenxia.com! Found {len(users)} users:")
        for u in users:
            print(f"- {u.get('primaryEmail')} ({u.get('name', {}).get('fullName')})")
    except Exception as e:
        print("Failed with subject brenxia@brenxia.com:", e)

if __name__ == "__main__":
    main()
