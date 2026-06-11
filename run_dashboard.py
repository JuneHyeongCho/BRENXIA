import time
import sys
import logging
from vibe_cording import PMAgent

# Setup logger to see output
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("run_dashboard")

def main():
    logger.info("Starting BRENXIA PM Agent Dashboard runner...")
    
    # Initialize PMAgent (is_mock=None auto-detects credentials.json)
    agent = PMAgent(db_path="data/db.json", is_mock=None)
    
    # Inject dummy projects if database is empty
    existing_projects = agent.db.list_projects()
    if not existing_projects:
        logger.info("Injecting dummy projects for visualization...")
        agent.request_project_creation(
            client_name="MasterCard",
            brand_name="MasterCard",
            project_name="MasterCard Q2 Launch Campaign",
            pm_email="lead_pm@brenxia.com",
            importance="Critical",
            pd_email="pd_planner@brenxia.com",
            cd_email="cd_creative@brenxia.com",
            members=["practitioner1@brenxia.com", "practitioner2@brenxia.com"]
        )
        agent.request_project_creation(
            client_name="WooRi Card",
            brand_name="WooRi",
            project_name="WooRi Card Standard Campaign",
            pm_email="lead_pm@brenxia.com",
            importance="Standard",
            pd_email="pd_planner@brenxia.com",
            cd_email="cd_creative@brenxia.com",
            members=["practitioner1@brenxia.com"]
        )
        
        # Change status for one of the projects to make dashboard interesting
        projects = agent.db.list_projects()
        if len(projects) > 1:
            agent.update_project_status(projects[1].project_id, "Execution")
            
    # Start dashboard
    agent.start_dashboard()
    print(f"\n==================================================")
    print(f"BRENXIA WPMS Dashboard is running!")
    print(f"Open your browser and visit: {agent.get_dashboard_url()}")
    print(f"==================================================\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down dashboard...")
        agent.stop_dashboard()
        sys.exit(0)

if __name__ == "__main__":
    main()
