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

# Send an initial message to confirm the new 2-hour reporting rule
if WEBHOOK_URL:
    try:
        requests.post(WEBHOOK_URL, json={"text": f"⏳ **[시스템 알림]** DNS 감시 레이더 설정 변경 완료. 지금부터 전파 완료 시까지 **2시간 간격**으로 생존(대기 중) 보고를 발송합니다."})
    except Exception as e:
        pass

last_notify_time = time.time()
notify_interval = 2 * 60 * 60  # 2 hours in seconds

while True:
    try:
        ip = socket.gethostbyname(domain)
        success_msg = f"🎉 **[긴급 알람]** BRENXIA DNS 연결 성공!\n`{domain}` 주소가 이제 VPS IP(`{ip}`)로 정상적으로 연결되었습니다. 본격적인 고도화 작업을 시작할 수 있습니다. 감시 레이더를 완전히 종료합니다."
        print(f"\n[{time.strftime('%X')}] SUCCESS! DNS propagation complete.")
        print(success_msg)
        
        if WEBHOOK_URL:
            try:
                requests.post(WEBHOOK_URL, json={"text": success_msg})
                print("Success webhook sent successfully.")
            except Exception as e:
                print(f"Failed to send success webhook: {e}")
            
        sys.exit(0)
    except socket.gaierror:
        current_time = time.time()
        # Check if 2 hours have passed
        if current_time - last_notify_time >= notify_interval:
            progress_msg = f"📡 **[정기 생존 보고]** DNS 전파 대기 중...\n아직 `{domain}` 주소가 전파되지 않아 10초 주기로 계속 감시 중입니다."
            print(f"\n[{time.strftime('%X')}] Sending 2-hour progress report...")
            if WEBHOOK_URL:
                try:
                    requests.post(WEBHOOK_URL, json={"text": progress_msg})
                except Exception as e:
                    print(f"Failed to send progress webhook: {e}")
            last_notify_time = current_time
            
        print(".", end="", flush=True)
        time.sleep(10)
