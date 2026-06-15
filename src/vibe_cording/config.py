import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    COMPANY_MASTER_EMAIL = os.environ.get("COMPANY_MASTER_EMAIL", "brenxia@brenxia.com")
    CEO_EMAIL = os.environ.get("CEO_EMAIL", "psyche@brenxia.com")
    
    # Path to Google Service Account Credentials JSON
    GOOGLE_CREDENTIALS_FILE = os.environ.get("GOOGLE_CREDENTIALS_FILE", "config/credentials.json")
    
    # Default shared drive root path or ID
    SHARED_DRIVE_ROOT_ID = os.environ.get("SHARED_DRIVE_ROOT_ID", "root")
    
    # Template ID for BRENXIA WPMS Google Spreadsheet
    WPMS_TEMPLATE_ID = os.environ.get("WPMS_TEMPLATE_ID", "template_spreadsheet_id")

