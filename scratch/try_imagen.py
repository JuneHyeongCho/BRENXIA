import os
import json
import base64
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def main():
    credentials_path = "config/credentials.json"
    if not os.path.exists(credentials_path):
        print(f"Credentials not found at {credentials_path}")
        return

    print("Loading credentials...")
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=scopes
    )
    
    print("Refreshing token...")
    credentials.refresh(Request())
    token = credentials.token
    project_id = credentials.project_id
    print(f"Project ID: {project_id}")

    # Endpoint URL (us-central1 is standard for Vertex AI)
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
                "prompt": "A sleek MasterCard credit card visual, glowing neon orange and red logo circles, dark luxury futuristic background, cinematic lighting, 8k resolution"
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "1:1",
            "outputMimeType": "image/png"
        }
    }

    print("Sending request to Vertex AI Imagen API...")
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error Response: {response.text}")
        return

    resp_json = response.json()
    predictions = resp_json.get("predictions", [])
    if not predictions:
        print("No predictions returned in response.")
        return

    # Extract base64 encoded image bytes
    img_b64 = predictions[0].get("bytesBase64Encoded")
    if not img_b64:
        print("No bytesBase64Encoded key in prediction.")
        return

    img_data = base64.b64decode(img_b64)
    output_path = "scratch/test_mastercard_neon.png"
    with open(output_path, "wb") as f:
        f.write(img_data)
    print(f"Success! Image saved to {output_path}")

if __name__ == "__main__":
    main()
