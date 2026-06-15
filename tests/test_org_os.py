import os
import shutil
import unittest
from datetime import datetime, timedelta
from vibe_cording import PMAgent, Project
from vibe_cording.models import AgentEntity, ResourceMM
from vibe_cording.org_os import PaperclipOS, HermesAgent

class TestOrgOS(unittest.TestCase):
    def setUp(self):
        self.db_path = "data/test_org_db.json"
        if os.path.exists("data"):
            shutil.rmtree("data")
        
        self.agent = PMAgent(db_path=self.db_path, is_mock=True)
        self.paperclip = self.agent.paperclip
        self.hermes = self.agent.hermes

    def tearDown(self):
        if os.path.exists("data"):
            shutil.rmtree("data")

    def test_approval_timeout_fallback(self):
        # Create a critical project that requires CEO approval
        project = self.agent.request_project_creation(
            client_name="TimeoutClient",
            brand_name="TimeoutBrand",
            project_name="TimeoutProj",
            pm_email="pm@brenxia.com",
            importance="Critical",
            pd_email="pd@brenxia.com",
            cd_email="cd@brenxia.com",
            members=[]
        )
        self.assertEqual(project.approval_status, "Pending")
        self.assertFalse(project.temporary_deploy)

        # Force created_at to 13 hours ago to trigger timeout
        project.created_at = (datetime.now() - timedelta(hours=13)).isoformat()
        self.agent.db.save_project(project)

        # Run timeout check
        triggered = self.hermes.check_approval_timeout(project.project_id)
        self.assertTrue(triggered)

        updated_project = self.agent.db.get_project(project.project_id)
        self.assertEqual(updated_project.approval_status, "Bypassed")
        self.assertTrue(updated_project.temporary_deploy)
        self.assertIn("[Unapproved]", updated_project.project_name)

    def test_resource_clean_up_rule(self):
        project = self.agent.request_project_creation(
            client_name="CleanClient",
            brand_name="CleanBrand",
            project_name="CleanProj",
            pm_email="pm@brenxia.com",
            importance="Standard",
            pd_email="pd@brenxia.com",
            cd_email="cd@brenxia.com",
            members=[]
        )
        self.assertEqual(project.status, "Proposal")

        # Force created_at to 49 hours ago to trigger cleanup
        project.created_at = (datetime.now() - timedelta(hours=49)).isoformat()
        self.agent.db.save_project(project)

        # Run cleanup check
        triggered = self.hermes.check_clean_up_rule(project.project_id)
        self.assertTrue(triggered)

        updated_project = self.agent.db.get_project(project.project_id)
        self.assertEqual(updated_project.status, "Lost")
        self.assertIn("Auto Clean-up", updated_project.lost_reason)

    def test_pms_number_null_only_validation(self):
        project = self.agent.request_project_creation(
            client_name="ValClient",
            brand_name="ValBrand",
            project_name="ValProj",
            pm_email="pm@brenxia.com",
            importance="Standard",
            pd_email="pd@brenxia.com",
            cd_email="cd@brenxia.com",
            members=[]
        )
        
        # Add a resource with None values
        res1 = ResourceMM(project.project_id, "ResourceNull", "Manager", None, "", 0.0)
        self.agent.db.save_resources([res1])

        # Validate numbers - should generate warnings
        warnings = self.hermes.validate_pms_numbers(project.project_id)
        self.assertTrue(any("ResourceNull" in w for w in warnings))

        # Update resource with 0 (which is explicitly allowed and should NOT trigger warning)
        res2 = ResourceMM(project.project_id, "ResourceZero", "Manager", 0.0, 0.0, 0.0)
        self.agent.db.save_resources([res2])

        warnings_zero = self.hermes.validate_pms_numbers(project.project_id)
        # Should not have warnings about ResourceZero
        self.assertFalse(any("ResourceZero" in w for w in warnings_zero))

    def test_auto_version_control_push_down(self):
        project = self.agent.request_project_creation(
            client_name="VersionClient",
            brand_name="VersionBrand",
            project_name="VersionProj",
            pm_email="pm@brenxia.com",
            importance="Standard",
            pd_email="pd@brenxia.com",
            cd_email="cd@brenxia.com",
            members=[]
        )

        # Standard upload - no confirmation card needed
        prompt = self.agent.handle_file_upload(project.project_id, "02.기획", "proposal_v0.1.pptx")
        self.assertIsNone(prompt)

        # Upload final draft - version matched, should return prompt
        prompt_final = self.agent.handle_file_upload(project.project_id, "02.기획", "proposal_final_v1.0.pptx")
        self.assertIsNotNone(prompt_final)
        self.assertIn("WBS status update", prompt_final)

    def test_human_bypass_rule(self):
        project = self.agent.request_project_creation(
            client_name="BypassClient",
            brand_name="BypassBrand",
            project_name="BypassProj",
            pm_email="pm@brenxia.com",
            importance="Standard",
            pd_email="pd@brenxia.com",
            cd_email="cd@brenxia.com",
            members=[]
        )
        
        # Advance project to step 4 (Strategy Formulation)
        project.step = 4
        self.agent.db.save_project(project)

        # Human PM directly uploads draft to '02.기획' - should bypass PD check
        self.hermes.handle_file_upload(project.project_id, "02.기획", "strategy_brief_v1.0.docx")

        updated_project = self.agent.db.get_project(project.project_id)
        # Should bypass step 4 and go to step 5
        self.assertEqual(updated_project.step, 5)

    def test_deadlock_resolution(self):
        project = self.agent.request_project_creation(
            client_name="DeadlockClient",
            brand_name="DeadlockBrand",
            project_name="DeadlockProj",
            pm_email="pm@brenxia.com",
            importance="Standard",
            pd_email="pd@brenxia.com",
            cd_email="cd@brenxia.com",
            members=[]
        )

        # Debate round 1 & 2
        res1 = self.hermes.trigger_debate(project.project_id, 5)
        self.assertFalse(res1)
        res2 = self.hermes.trigger_debate(project.project_id, 5)
        self.assertFalse(res2)

        # Debate round 3 - deadlock resolution triggered
        res3 = self.hermes.trigger_debate(project.project_id, 5)
        self.assertTrue(res3)

    def test_reverse_routing(self):
        project = self.agent.request_project_creation(
            client_name="RoutingClient",
            brand_name="RoutingBrand",
            project_name="RoutingProj",
            pm_email="pm@brenxia.com",
            importance="Standard",
            pd_email="pd@brenxia.com",
            cd_email="cd@brenxia.com",
            members=[]
        )
        project.step = 9 # Proposal & Approval step
        self.agent.db.save_project(project)

        # Feedback Level 1 -> step 7
        self.hermes.handle_reverse_routing(project.project_id, 1)
        self.assertEqual(self.agent.db.get_project(project.project_id).step, 7)

        # Feedback Level 2 -> step 6
        self.hermes.handle_reverse_routing(project.project_id, 2)
        self.assertEqual(self.agent.db.get_project(project.project_id).step, 6)

        # Feedback Level 3 -> step 4
        self.hermes.handle_reverse_routing(project.project_id, 3)
        self.assertEqual(self.agent.db.get_project(project.project_id).step, 4)

    def test_hybrid_agent_expansion_option_a(self):
        project = self.agent.request_project_creation(
            client_name="ExpandClient",
            brand_name="ExpandBrand",
            project_name="ExpandProj",
            pm_email="pm@brenxia.com",
            importance="Standard",
            pd_email="pd@brenxia.com",
            cd_email="cd@brenxia.com",
            members=[]
        )

        # Expand system with custom copywriter
        new_agent = self.hermes.trigger_hybrid_expansion(project.project_id, "Translator", "A")
        self.assertIsNotNone(new_agent)
        self.assertEqual(new_agent.role, "Translator")
        
        # Verify stored in DB
        saved_agent = self.agent.db.get_agent(new_agent.agent_id)
        self.assertIsNotNone(saved_agent)
        self.assertEqual(saved_agent.name, "Custom Translator")

if __name__ == "__main__":
    unittest.main()
