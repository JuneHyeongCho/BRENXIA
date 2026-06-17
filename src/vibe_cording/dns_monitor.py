import time
import socket
import sys
import requests
import os
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.environ.get("GOOGLE_CHAT_WEBHOOK_URL")

domain = "agent.brenxia.com"
print(f"[{time.strftime('%X')}] Starting DNS propagation monitor for {domain}...")

while True:
    try:
        ip = socket.gethostbyname(domain)
        success_msg = f"🎉 **[긴급 알람]** BRENXIA DNS 연결 성공!\n`{domain}` 주소가 이제 VPS IP(`{ip}`)로 정상적으로 연결되었습니다. 본격적인 고도화 작업을 시작할 수 있습니다."
        print(f"\n[{time.strftime('%X')}] SUCCESS! DNS propagation complete.")
        print(success_msg)
        
        if WEBHOOK_URL:
            requests.post(WEBHOOK_URL, json={"text": success_msg})
            print("Webhook sent successfully.")
            
        sys.exit(0)
    except socket.gaierror:
        print(".", end="", flush=True)
        time.sleep(10)
