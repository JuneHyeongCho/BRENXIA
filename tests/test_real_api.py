import os
import sys
import logging
from vibe_cording import PMAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("test_real_api")

def test_integration():
    logger.info("Starting BRENXIA PM Agent Real Google API Integration Test...")
    
    # Ensure credentials file is in place
    credentials_path = "config/credentials.json"
    if not os.path.exists(credentials_path):
        logger.error(f"Credentials file not found at: {credentials_path}. Please place it there before running.")
        sys.exit(1)
        
    # Initialize agent - it will auto-detect credentials.json and run in REAL mode
    agent = PMAgent(db_path="data/real_db.json")
    
    if agent.is_mock:
        logger.error("Agent failed to initialize in REAL mode. Running in mock fallback mode. Please check config/credentials.json.")
        sys.exit(1)

    logger.info("PMAgent successfully initialized in REAL Google API mode.")
    
    # Requesting project creation - this will attempt to create folders on Google Drive
    try:
        project = agent.request_project_creation(
            client_name="MasterCard_Test",
            brand_name="MasterCard",
            project_name="Korean Folder Test 1",
            pm_email="@\uc870\uc900\ud615", # CEO @조준형
            importance="Standard",
            pd_email="@\ubc15\uc900\ud615", # PD @박준형
            cd_email="@\uc774\uc11d\uc6b0", # CD @이석우
            members=[]
        )
        logger.info(f"Successfully created project '{project.project_name}' with ID '{project.project_id}'")
        logger.info(f"Resolved PM Name: {project.pm_name}, Email: {project.pm_email}")
        logger.info(f"Resolved PD Name: {project.pd_name}, Email: {project.pd_email}")
        logger.info(f"Resolved CD Name: {project.cd_name}, Email: {project.cd_email}")

        # Run Sheets API batch read sync check
        logger.info("Running sync check from live Spreadsheet...")
        synced_project = agent.sync_project_from_spreadsheet(project.project_id)
        logger.info(f"Synced Project Client: {synced_project.client_name}, Project Name: {synced_project.project_name}")
        logger.info(f"Synced Project PD: {synced_project.pd_name} ({synced_project.pd_email})")
        logger.info(f"Synced Project CD: {synced_project.cd_name} ({synced_project.cd_email})")
        logger.info(f"Synced Project Predicted Sales: {synced_project.predicted_sales}")
        logger.info(f"Check your Google Shared Drive for folder: 260611_MasterCard_Test_MasterCard_API Integration Test Run 7 (Drive Folder ID: {project.drive_folder_id})")
    except Exception as e:
        logger.error(f"Failed to execute real Google Drive/Sheets API operations: {e}")
        logger.error("Please ensure the Service Account email has been added to your Shared Drive with 'Manager' or 'Content Manager' permissions.")
        sys.exit(1)

if __name__ == "__main__":
    test_integration()
