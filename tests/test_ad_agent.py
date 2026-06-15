import os
import shutil
import unittest
from unittest.mock import patch, Mock
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

    @patch.dict(os.environ, {"GEMINI_API_KEY": ""})
    def test_generate_prompt_config_mastercard(self):
        config = self.agent.generate_prompt_config("Create a visual for MasterCard credit cards.")
        self.assertIn("MasterCard orange and red circles", config["positive_prompt"])
        self.assertEqual(config["width"], 1024)
        self.assertEqual(config["height"], 1024)

    @patch.dict(os.environ, {"GEMINI_API_KEY": ""})
    def test_generate_prompt_config_woori(self):
        config = self.agent.generate_prompt_config("Visual proposal for Woori card campaign.")
        self.assertIn("WooRi Card corporate blue identity", config["positive_prompt"])

    @patch.dict(os.environ, {"GEMINI_API_KEY": ""})
    def test_generate_prompt_config_default(self):
        config = self.agent.generate_prompt_config("Some generic brief.")
        self.assertIn("artistic illustration", config["positive_prompt"])

    @patch("requests.post")
    @patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
    def test_generate_prompt_config_gemini_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": "dynamic prompt from gemini"
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response

        config = self.agent.generate_prompt_config("test brief")
        self.assertEqual(config["positive_prompt"], "dynamic prompt from gemini")

    def test_generate_mock_visual_draft(self):
        config = self.agent.generate_prompt_config("test")
        out_path = os.path.join(self.test_dir, "draft.png")
        result_path = self.agent.generate_mock_visual_draft(config, out_path)
        
        self.assertEqual(result_path, out_path)
        self.assertTrue(os.path.exists(out_path))
        with open(out_path, "rb") as f:
            self.assertEqual(f.read(), b"MOCK_PNG_DATA_FOR_AD_AGENT_VISUAL_DRAFT")

    @patch("requests.get")
    @patch.dict(os.environ, {"GEMINI_API_KEY": ""})
    def test_generate_visual_draft_mock_fallback(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        config = self.agent.generate_prompt_config("test")
        out_path = os.path.join(self.test_dir, "real_draft.png")
        result_path = self.agent.generate_visual_draft(config, out_path)
        
        self.assertEqual(result_path, out_path)
        self.assertTrue(os.path.exists(out_path))
        with open(out_path, "rb") as f:
            self.assertEqual(f.read(), b"MOCK_PNG_DATA_FOR_AD_AGENT_VISUAL_DRAFT")

if __name__ == "__main__":
    unittest.main()
