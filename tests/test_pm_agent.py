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

    def test_project_creation_missing_directors_raises_error(self):
        with self.assertRaises(ValueError):
            self.agent.request_project_creation(
                client_name="TestClient",
                brand_name="TestBrand",
                project_name="TestProject",
                pm_email="pm@brenxia.com",
                importance="Standard",
                pd_email="",
                cd_email="cd@brenxia.com",
                members=[]
            )

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
        prompt = self.agent.handle_file_upload(project.project_id, "02.Planning", "proposal_v0.1.pptx")
        self.assertIsNone(prompt)

        # Upload final file triggers review prompt
        prompt_final = self.agent.handle_file_upload(project.project_id, "02.Planning", "proposal_final.pptx")
        self.assertIsNotNone(prompt_final)
        self.assertIn("Review Pending", prompt_final)

if __name__ == "__main__":
    unittest.main()
