import os
from typing import Any

class Config:
    def __init__(self) -> None:
        self.GOOGLE_CREDENTIALS_FILE = os.environ.get(
            "GOOGLE_CREDENTIALS_FILE", "google_credentials.json"
        )
        self.GOOGLE_CHAT_USER_CLIENT_SECRET_FILE = os.environ.get(
            "GOOGLE_CHAT_USER_CLIENT_SECRET_FILE", "google_chat_user_client_secret.json"
        )
        self.COMPANY_MASTER_EMAIL = os.environ.get(
            "COMPANY_MASTER_EMAIL", "brenxia@brenxia.com"
        )
        self.CEO_EMAIL = os.environ.get(
            "CEO_EMAIL", "psyche@brenxia.com"
        )
        self.SHARED_DRIVE_ROOT_ID = os.environ.get(
            "SHARED_DRIVE_ROOT_ID", "root"
        )
        self.WPMS_TEMPLATE_ID = os.environ.get(
            "WPMS_TEMPLATE_ID", "1nnv1bV5bUfe-fjdJh8OWPQYdob0HBhttRgCDNjwHmPA"
        )
        self.DASHBOARD_HOST = os.environ.get(
            "DASHBOARD_HOST", "0.0.0.0"
        )
        self.DASHBOARD_PORT = int(os.environ.get(
            "DASHBOARD_PORT", "8000"
        ))
        # Default to True for safe development, set to False explicitly in .env for real calls
        self.MOCK_MODE = os.environ.get("MOCK_MODE", "True").lower() == "true"
