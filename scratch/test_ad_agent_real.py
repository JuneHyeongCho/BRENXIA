import os
import sys
import logging
from vibe_cording import PMAgent, ADAgent

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("test_ad_agent_real")

def main():
    logger.info("Starting AD Agent Real API Image Generation Test...")
    
    # 1. Initialize PM Agent to load credentials and setup workspace client
    logger.info("Initializing PM Agent to get workspace credentials...")
    pm_agent = PMAgent(db_path="data/test_db_real.json")
    
    if pm_agent.is_mock:
        logger.warning("PM Agent running in MOCK mode (config/credentials.json not found).")
        logger.warning("Testing with mock fallback image generation.")
    else:
        logger.info("PM Agent successfully initialized in REAL mode.")

    # 2. Initialize AD Agent with the workspace client
    ad_agent = ADAgent(workspace_client=pm_agent.workspace)

    # 3. Generate prompt configuration from a creative brief
    brief = "A sleek MasterCard credit card visual, glowing neon orange and red logo circles, dark luxury futuristic background, cinematic lighting, 8k resolution"
    logger.info(f"Generating prompt from creative brief: '{brief}'")
    prompt_config = ad_agent.generate_prompt_config(brief)
    
    logger.info(f"Generated Prompt Config: {prompt_config}")

    # 4. Generate visual draft
    output_image_path = "scratch/visual_draft_mastercard.png"
    logger.info(f"Requesting image generation. Saving to: {output_image_path}")
    
    result_path = ad_agent.generate_visual_draft(prompt_config, output_image_path)
    
    if os.path.exists(result_path):
        logger.info(f"Success! Image generated successfully at: {result_path}")
        # Print file size to confirm it is not empty
        file_size = os.path.getsize(result_path)
        logger.info(f"Generated image file size: {file_size} bytes")
    else:
        logger.error("Failed to generate image file. File does not exist.")
        sys.exit(1)

if __name__ == "__main__":
    main()
