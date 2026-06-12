import os
import shutil
import unittest
from vibe_cording import ADAgent

class TestADAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ADAgent()
        self.test_dir = "data/test_scratch"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_generate_prompt_config_mastercard(self):
        config = self.agent.generate_prompt_config("Create a visual for MasterCard credit cards.")
        self.assertIn("MasterCard orange and red circles", config["positive_prompt"])
        self.assertEqual(config["width"], 1024)
        self.assertEqual(config["height"], 1024)

    def test_generate_prompt_config_woori(self):
        config = self.agent.generate_prompt_config("Visual proposal for Woori card campaign.")
        self.assertIn("WooRi Card corporate blue identity", config["positive_prompt"])

    def test_generate_prompt_config_default(self):
        config = self.agent.generate_prompt_config("Some generic brief.")
        self.assertIn("artistic illustration", config["positive_prompt"])

    def test_generate_mock_visual_draft(self):
        config = self.agent.generate_prompt_config("test")
        out_path = os.path.join(self.test_dir, "draft.png")
        result_path = self.agent.generate_mock_visual_draft(config, out_path)
        
        self.assertEqual(result_path, out_path)
        self.assertTrue(os.path.exists(out_path))
        with open(out_path, "rb") as f:
            self.assertEqual(f.read(), b"MOCK_PNG_DATA_FOR_AD_AGENT_VISUAL_DRAFT")

if __name__ == "__main__":
    unittest.main()
