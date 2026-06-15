# BRENXIA 에이전트 VPS 배포 가이드 (VPS Deployment Guide)

이 문서는 호스팅어(Hostinger) 가상 사설 서버(VPS) 환경에서 헤르메스 에이전트(Hermes Agent) 및 페이퍼클립 OS(Paperclip OS) 대시보드 서버를 구동하기 위한 배포 지침서입니다.

두 가지 구동 방식(Lightweight `uv` 직접 구동 방식, Docker 컨테이너 구동 방식)을 제공합니다.

---

## 1. 사전 요구사항 (Prerequisites)

* **서버 IP**: `72.62.65.177`
* **OS**: `Ubuntu 22.04 LTS` 또는 `Ubuntu 24.04 LTS` (권장)
* **접속 권한**: `root` 관리자 권한 및 비밀번호(또는 SSH Key)

---

## 2. Docker 컨테이너 배포 방식 (Docker Compose Deployment) - 권장 🌟

도커(Docker)를 활용하면 리눅스 서버에 파이썬 설치나 의존성 충돌 걱정 없이 컨테이너화하여 매우 깔끔하고 안전하게 운영할 수 있습니다.

### ① SSH를 이용한 서버 접속 및 패키지 설치
본인의 PC 터미널을 열고 서버에 원격 접속 후 Docker를 설치합니다.
```bash
ssh root@72.62.65.177
```

### ② 도커 및 도커 컴포즈 설치 (Docker Install)
우분투 서버에 도커 엔진을 즉시 설치해 주는 호스팅어/우분투 공식 스크립트를 가동합니다.
```bash
# Docker 공식 설치 스크립트 실행
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker 서비스 활성화 및 시작
sudo systemctl enable docker
sudo systemctl start docker
```

### ③ 깃허브 저장소 클론 (Code Download)
작성된 최신 소스 코드를 서버로 내려받습니다.
```bash
sudo apt-get install -y git
git clone https://github.com/JuneHyeongCho/BRENXIA.git
cd BRENXIA
```

### ④ 환경 설정 파일 작성 (.env)
도커 컨테이너 내부로 주입할 설정값을 지정합니다.
```bash
nano .env
```
아래 설정을 복사해 붙여넣고 저장합니다. (저장 단축키: `Ctrl + O` ➡️ Enter ➡️ 종료: `Ctrl + X`)
```env
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8000
COMPANY_MASTER_EMAIL=brenxia@brenxia.com
CEO_EMAIL=psyche@brenxia.com
```

### ⑤ 컨테이너 빌드 및 백그라운드 기동
```bash
# docker-compose.yml 설정을 기반으로 백그라운드(-d) 빌드 및 기동
docker compose up -d --build
```

### ⑥ 동작 상태 확인 및 로그 검토
```bash
# 도커 컨테이너 동작 상태 확인
docker ps

# 컨테이너 실시간 가동 로그 확인
docker logs -f brenxia-agent
```
정상 작동이 확인되면 인터넷 브라우저에서 `http://72.62.65.177:8000`으로 바로 대시보드 조회가 가능합니다.

---

## 3. Lightweight `uv` 직접 구동 방식 (Direct Run with UV)

도커를 사용하지 않고 우분투 가상 머신 위에 파이썬 환경을 가볍게 즉시 빌드하여 가동하는 방식입니다.

### ① SSH 서버 접속
```bash
ssh root@72.62.65.177
```

### ② 기본 도구 및 uv 가상환경 관리자 설치
```bash
sudo apt-get update && sudo apt-get install -y git curl
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### ③ 소스 코드 다운로드 및 스크립트 실행
```bash
git clone https://github.com/JuneHyeongCho/BRENXIA.git
cd BRENXIA
chmod +x scripts/deploy_vps.sh
./scripts/deploy_vps.sh
```

---

## 4. 구동 중단 및 관리 (Server Administration)

### ① 도커(Docker) 중단 및 재시작
```bash
# 컨테이너 서비스 중지
docker compose down

# 컨테이너 서비스 재시작
docker compose restart
```

### ② `uv` 직접 구동 방식 중단
```bash
# 백그라운드로 돌아가고 있는 python 프로세스 종료
pkill -f run_dashboard.py
```
