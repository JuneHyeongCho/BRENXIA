import os
import unittest
import shutil
from vibe_cording import PMAgent, Project

class TestPMAgent(unittest.TestCase):
    def setUp(self):
        self.db_path = "data/test_db.json"
        # Ensure test directory is clean
        if os.path.exists("data"):
            shutil.rmtree("data")
        self.agent = PMAgent(db_path=self.db_path, is_mock=True)

    def tearDown(self):
        # Clean up database files
        if os.path.exists("data"):
            shutil.rmtree("data")

    def test_hello(self):
        from vibe_cording import hello
        self.assertEqual(hello(), "Hello from BRENXIA Agent!")

    def test_project_creation_standard(self):
        project = self.agent.request_project_creation(
            client_name="TestClient",
            brand_name="TestBrand",
            project_name="TestProject",
            pm_email="pm@brenxia.com",
            importance="Standard",
            pd_email="pd@brenxia.com",
            cd_email="cd@brenxia.com",
            members=["practitioner1@brenxia.com"]
        )
        self.assertIsNotNone(project.project_id)
        self.assertEqual(project.status, "Proposal")
        self.assertEqual(project.importance, "Standard")
        self.assertEqual(project.pd_email, "pd@brenxia.com")
        self.assertEqual(project.cd_email, "cd@brenxia.com")
        
        # Verify saved in db
        saved_project = self.agent.db.get_project(project.project_id)
        self.assertIsNotNone(saved_project)
        self.assertEqual(saved_project.project_name, "TestProject")

    def test_project_creation_missing_directors_no_longer_raises_error(self):
        project = self.agent.request_project_creation(
            client_name="TestClient",
            brand_name="TestBrand",
            project_name="TestProject",
            pm_email="pm@brenxia.com",
            importance="Standard",
            pd_email="",
            cd_email="cd@brenxia.com",
            members=[]
        )
        self.assertIsNotNone(project.project_id)
        self.assertEqual(project.pd_email, "")

    def test_project_status_transitions(self):
        project = self.agent.request_project_creation(
            client_name="TestClient",
            brand_name="TestBrand",
            project_name="TestProject",
            pm_email="pm@brenxia.com",
            importance="Standard",
            pd_email="pd@brenxia.com",
            cd_email="cd@brenxia.com",
            members=[]
        )
        self.agent.update_project_status(project.project_id, "Execution")
        updated_project = self.agent.db.get_project(project.project_id)
        self.assertEqual(updated_project.status, "Execution")

    def test_file_upload_version_control(self):
        project = self.agent.request_project_creation(
            client_name="TestClient",
            brand_name="TestBrand",
            project_name="TestProject",
            pm_email="pm@brenxia.com",
            importance="Standard",
            pd_email="pd@brenxia.com",
            cd_email="cd@brenxia.com",
            members=[]
        )
        # Normal upload
        prompt = self.agent.handle_file_upload(project.project_id, "02.\uae30\ud68d", "proposal_v0.1.pptx")
        self.assertIsNone(prompt)

        # Upload final file triggers review prompt
        prompt_final = self.agent.handle_file_upload(project.project_id, "02.\uae30\ud68d", "proposal_final.pptx")
        self.assertIsNotNone(prompt_final)
        self.assertIn("Review Pending", prompt_final)

    def test_resolve_member(self):
        # 1. Test live matching from default list
        name, email = self.agent.resolve_member("@\uc774\uc11d\uc6b0")
        self.assertEqual(name, "\uc774\uc11d\uc6b0")
        self.assertEqual(email, "249@brenxia.com")
        
        name2, email2 = self.agent.resolve_member("\uc870\uc900\ud615")
        self.assertEqual(name2, "\uc870\uc900\ud615")
        self.assertEqual(email2, "psyche@brenxia.com")
        
        # 2. Test email input reverse lookup
        name3, email3 = self.agent.resolve_member("charon@brenxia.com")
        self.assertEqual(name3, "\ubc15\uc900\ud615")
        self.assertEqual(email3, "charon@brenxia.com")

        # 3. Test fallback
        name4, email4 = self.agent.resolve_member("@testuser")
        self.assertEqual(name4, "testuser")
        self.assertEqual(email4, "testuser@brenxia.com")

    def test_sync_project_from_spreadsheet(self):
        project = self.agent.request_project_creation(
            client_name="OldClient",
            brand_name="OldBrand",
            project_name="OldProject",
            pm_email="pm@brenxia.com",
            importance="Standard",
            pd_email="@\uc870\uc900\ud615",
            cd_email="@\uc774\uc11d\uc6b0",
            members=[]
        )
        # Mock spreadsheet ID
        project.spreadsheet_id = "mock_spreadsheet_id"
        self.agent.db.save_project(project)
        
        # Call sync
        synced_project = self.agent.sync_project_from_spreadsheet(project.project_id)
        
        # Verify fields synced from mock values inside read_pms_cells
        self.assertEqual(synced_project.client_name, "MockClient")
        self.assertEqual(synced_project.project_name, "MockProject")
        self.assertEqual(synced_project.pd_name, "\uc870\uc900\ud615")
        self.assertEqual(synced_project.pd_email, "psyche@brenxia.com")
        self.assertEqual(synced_project.cd_name, "\uc774\uc11d\uc6b0")
        self.assertEqual(synced_project.cd_email, "249@brenxia.com")
        self.assertEqual(synced_project.predicted_sales, 1500000000)
        self.assertEqual(synced_project.predicted_purchases, "=C10*70%")
        # Verify members list mined from E65:E74 (contains '이석우' and '박준형')
        self.assertIn("249@brenxia.com", synced_project.members)
        self.assertIn("charon@brenxia.com", synced_project.members)

if __name__ == "__main__":
    unittest.main()
