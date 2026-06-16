import os
import logging
import requests
import base64
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
        Uses Gemini 2.5 Flash text API if GEMINI_API_KEY is available.
        """
        logger.info("Generating prompt configuration from creative brief.")
        positive_prompt = "premium brand campaign visual"
        
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                # Use active gemini-2.5-flash model
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
                headers = {"Content-Type": "application/json; charset=utf-8"}
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": f"Analyze this creative brief and generate a single highly detailed, professional visual prompt in English for image generation. The prompt should capture key brand elements, style, lighting, and composition. Brief: '{brief_text}'. Return ONLY the prompt text and nothing else."
                        }]
                    }]
                }
                
                logger.info("[REAL] Calling Gemini 2.5 Flash API to generate prompt...")
                response = requests.post(url, headers=headers, json=payload, timeout=20)
                if response.status_code == 200:
                    resp_json = response.json()
                    candidates = resp_json.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        if text:
                            positive_prompt = text
                            logger.info(f"[REAL] Gemini successfully generated prompt: {positive_prompt[:60]}...")
                else:
                    logger.warning(f"Gemini API returned status code {response.status_code}: {response.text}")
            except Exception as e:
                logger.error(f"Failed to generate prompt via Gemini API: {e}")
                logger.info("Falling back to rule-based prompt matching.")
        
        if not gemini_api_key or positive_prompt == "premium brand campaign visual":
            # Rule-based fallback
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

    def generate_visual_draft(self, prompt_config: Dict[str, Any], output_path: str = "scratch/visual_draft.png") -> str:
        """
        Calls Picsum Photos (free image API), Google AI Studio Gemini API, or Vertex AI Imagen API.
        """
        # 1. Try free Picsum Photos image API (No billing required, downloads real valid high-res image)
        try:
            url = "https://picsum.photos/1024"
            logger.info(f"[FREE] Requesting visual draft from Picsum Photos (width: 1024, height: 1024)...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                dir_name = os.path.dirname(output_path)
                if dir_name and not os.path.exists(dir_name):
                    os.makedirs(dir_name)
                    
                with open(output_path, "wb") as f:
                    f.write(response.content)
                    
                logger.info(f"[FREE] Image successfully generated and saved to: {output_path}")
                return output_path
            
            logger.warning(f"Picsum Photos API returned status code {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to generate image via Picsum Photos: {e}")
            logger.info("Falling back to Google AI Studio / Vertex AI / Mock.")

        # 2. Try Google AI Studio Imagen API if GEMINI_API_KEY is available (Fallback)
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                model_id = "imagen-4.0-generate-001"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:predict?key={gemini_api_key}"
                
                headers = {
                    "Content-Type": "application/json; charset=utf-8"
                }
                
                data = {
                    "instances": [
                        {
                            "prompt": prompt_config.get("positive_prompt", "")
                        }
                    ],
                    "parameters": {
                        "sampleCount": 1,
                        "aspectRatio": "1:1",
                        "outputMimeType": "image/png"
                    }
                }
                
                logger.info(f"[REAL] Requesting image generation from Google AI Studio Imagen model: {model_id}")
                response = requests.post(url, headers=headers, json=data, timeout=35)
                
                if response.status_code == 200:
                    resp_json = response.json()
                    predictions = resp_json.get("predictions", [])
                    if predictions:
                        img_b64 = predictions[0].get("bytesBase64Encoded")
                        if img_b64:
                            img_data = base64.b64decode(img_b64)
                            dir_name = os.path.dirname(output_path)
                            if dir_name and not os.path.exists(dir_name):
                                os.makedirs(dir_name)
                            with open(output_path, "wb") as f:
                                f.write(img_data)
                            logger.info(f"[REAL] Image successfully generated via Google AI Studio and saved to: {output_path}")
                            return output_path
                
                logger.warning(f"Google AI Studio Imagen API call failed with status code {response.status_code}: {response.text}")
            except Exception as e:
                logger.error(f"Failed to generate image via Google AI Studio: {e}")
                logger.info("Falling back to Vertex AI / Mock generation.")

        # 3. Fallback to Vertex AI or Mock generation
        if not self.workspace or getattr(self.workspace, "is_mock", True):
            logger.info("Workspace is in MOCK mode. Generating mock draft.")
            return self.generate_mock_visual_draft(prompt_config, output_path)

        try:
            # Get authenticated credentials from Google Workspace client
            credentials = self.workspace.credentials
            
            # Refresh credentials to get access token
            from google.auth.transport.requests import Request
            credentials.refresh(Request())
            token = credentials.token
            project_id = credentials.project_id
            
            region = "us-central1"
            model_id = "imagen-3.0-generate-002"
            url = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/publishers/google/models/{model_id}:predict"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            data = {
                "instances": [
                    {
                        "prompt": prompt_config.get("positive_prompt", "")
                    }
                ],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": "1:1",
                    "outputMimeType": "image/png"
                }
            }
            
            logger.info(f"[REAL] Requesting image generation from Vertex AI Imagen for project: {project_id}")
            response = requests.post(url, headers=headers, json=data, timeout=35)
            
            if response.status_code != 200:
                raise ValueError(f"Vertex AI API call failed with status code {response.status_code}: {response.text}")
                
            resp_json = response.json()
            predictions = resp_json.get("predictions", [])
            if not predictions:
                raise ValueError("No predictions returned from Vertex AI Imagen API.")
                
            img_b64 = predictions[0].get("bytesBase64Encoded")
            if not img_b64:
                raise ValueError("No base64 encoded image bytes in API response.")
                
            img_data = base64.b64decode(img_b64)
            
            # Ensure output directory exists
            dir_name = os.path.dirname(output_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)
                
            with open(output_path, "wb") as f:
                f.write(img_data)
                
            logger.info(f"[REAL] Image successfully generated and saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate real image via Vertex AI: {e}")
            logger.info("Falling back to mock visual draft generation.")
            return self.generate_mock_visual_draft(prompt_config, output_path)

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
