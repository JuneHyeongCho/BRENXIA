import os
import unittest
import shutil
from vibe_cording.pm_agent import PMAgent
from vibe_cording.models import Project

class TestPMAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.test_db_dir = "tests/data"
        self.test_db_path = os.path.join(self.test_db_dir, "test_db.json")
        if os.path.exists(self.test_db_dir):
            shutil.rmtree(self.test_db_dir)
        os.makedirs(self.test_db_dir, exist_ok=True)
        # Initialize PMAgent with mock mode active
        self.agent = PMAgent(db_path=self.test_db_path, is_mock=True)

    def tearDown(self) -> None:
        if os.path.exists(self.test_db_dir):
            shutil.rmtree(self.test_db_dir)

    def test_project_creation_mock(self) -> None:
        # Request project creation in simulation mode
        project = self.agent.request_project_creation(
            client_name="TestClient",
            brand_name="TestBrand",
            project_name="TestProject",
            pm_email="pm@brenxia.com",
            pd_email="pd@brenxia.com",
            cd_email="cd@brenxia.com",
            members=["member1@brenxia.com"],
            predicted_sales=1000.0,
            predicted_purchases=500.0,
            period_start="260617",
            period_end="261231",
            business_sector="Digital Marketing",
            department="Creative Team"
        )

        # Verify that project has generated ID and fields
        self.assertIsNotNone(project.project_id)
        self.assertEqual(project.client_name, "TestClient")
        self.assertEqual(project.status, "Proposal")
        self.assertEqual(project.drive_folder_id, f"mock_{project.project_id}_root_id")
        self.assertEqual(project.spreadsheet_id, "mock_TestClient_pms_spreadsheet_id")

        # Verify it exists in local DB
        fetched_project = self.agent.db.get_project(project.project_id)
        self.assertIsNotNone(fetched_project)
        self.assertEqual(fetched_project.client_name, "TestClient")
        self.assertEqual(fetched_project.spreadsheet_id, "mock_TestClient_pms_spreadsheet_id")

    def test_share_deliverable_mock(self) -> None:
        # Create project first
        project = self.agent.request_project_creation(
            client_name="TestClient",
            brand_name="TestBrand",
            project_name="TestProject",
            pm_email="pm@brenxia.com"
        )

        # Share dummy file in simulation mode
        dummy_file_path = os.path.join(self.test_db_dir, "dummy.txt")
        with open(dummy_file_path, "w") as f:
            f.write("dummy content")

        # Share to strategic category (e.g. "\uc81c\uc791" which maps to Unicode escape internally)
        result = self.agent.share_deliverable(
            project_id=project.project_id,
            file_path=dummy_file_path,
            category="\uc81c\uc791"
        )

        self.assertEqual(result["filename"], "dummy.txt")
        self.assertTrue(result["web_view_link"].startswith("https://drive.google.com/open?id="))

if __name__ == "__main__":
    unittest.main()
