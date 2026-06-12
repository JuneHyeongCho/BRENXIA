import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("vibe_cording.ad_agent")

class ADAgent:
    def __init__(self, workspace_client=None):
        """
        Initializes the AD Agent.
        """
        self.workspace = workspace_client

    def generate_prompt_config(self, brief_text: str) -> Dict[str, Any]:
        """
        Parses creative brief and generates optimal prompt JSON structure.
        """
        logger.info("Generating prompt configuration from creative brief.")
        positive_prompt = "premium brand campaign visual"
        
        lower_brief = brief_text.lower()
        if "mastercard" in lower_brief:
            positive_prompt += ", MasterCard orange and red circles, sleek credit card design, cinematic lighting"
        elif "woori" in lower_brief:
            positive_prompt += ", WooRi Card corporate blue identity, professional finance look, modern abstract pattern"
        else:
            positive_prompt += ", artistic illustration, high quality, 8k resolution"

        return {
            "positive_prompt": positive_prompt,
            "negative_prompt": "ugly, blurry, low quality, distorted, extra limbs, bad anatomy",
            "width": 1024,
            "height": 1024,
            "steps": 30,
            "cfg_scale": 7.5
        }

    def generate_mock_visual_draft(self, prompt_config: Dict[str, Any], output_path: str = "scratch/visual_draft.png") -> str:
        """
        Simulates image generation API call by writing a mock file to disk.
        """
        logger.info(f"Generating mock visual draft at path: {output_path}")
        
        dir_name = os.path.dirname(output_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(output_path, "wb") as f:
            f.write(b"MOCK_PNG_DATA_FOR_AD_AGENT_VISUAL_DRAFT")

        return output_path
