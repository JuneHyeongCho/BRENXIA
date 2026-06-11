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
            project_name="API Integration Test Run",
            pm_email="psyche@brenxia.com", # CEO email as test PM
            importance="Standard",
            pd_email="pd_planner@brenxia.com",
            cd_email="cd_creative@brenxia.com",
            members=[]
        )
        logger.info(f"Successfully ran integration check! Created project '{project.project_name}' with ID '{project.project_id}'")
        logger.info(f"Check your Google Shared Drive for folder: 260611_MasterCard_Test_MasterCard_API Integration Test Run (Drive Folder ID: {project.drive_folder_id})")
    except Exception as e:
        logger.error(f"Failed to execute real Google Drive API operations: {e}")
        logger.error("Please ensure the Service Account email has been added to your Shared Drive with 'Manager' or 'Content Manager' permissions.")
        sys.exit(1)

if __name__ == "__main__":
    test_integration()
