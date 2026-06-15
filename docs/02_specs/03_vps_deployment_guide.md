# BRENXIA 에이전트 VPS 배포 가이드 (VPS Deployment Guide)

이 문서는 호스팅어(Hostinger) 가상 사설 서버(VPS) 환경에서 헤르메스 에이전트(Hermes Agent) 및 페이퍼클립 OS(Paperclip OS) 대시보드 서버를 백그라운드 서비스(Background Service)로 구동하기 위한 배포 지침서입니다.

---

## 1. 사전 요구사항 (Prerequisites)

* **서버 IP**: `72.62.65.177`
* **OS**: `Ubuntu 22.04 LTS` 또는 `Ubuntu 24.04 LTS` (권장)
* **접속 권한**: `root` 관리자 권한 및 비밀번호(또는 SSH Key)

---

## 2. 배포 및 구동 단계 (Deployment Steps)

터미널 창을 열고 아래 명령어를 순서대로 복사하여 실행해 주시기 바랍니다.

### ① SSH를 이용한 서버 접속
본인의 PC 터미널(Windows PowerShell 또는 CMD)을 열고 서버에 원격 접속합니다.
```bash
ssh root@72.62.65.177
```
> [!NOTE]
> 처음 접속 시 authenticity 관련 경고가 뜨면 `yes`를 입력하고 설정해 두신 비밀번호를 입력합니다.

### ② 시스템 패키지 업데이트 및 필수 도구 설치
리눅스 서버의 기본 소프트웨어를 최신화하고 코드 다운로드를 위한 Git과 웹 연결 도구(curl)를 설치합니다.
```bash
sudo apt-get update && sudo apt-get install -y git curl
```

### ③ Astral `uv` 설치 (Python 가상 환경 관리자)
BRENXIA 프로젝트는 파이썬 3.14.6 버전을 사용합니다. `uv` 도구를 설치하면 시스템 복잡한 설정 없이도 필요한 파이썬 버전을 서버가 자동으로 다운로드하고 가상환경을 구축해 줍니다.
```bash
# uv 설치 스크립트 실행
curl -LsSf https://astral.sh/uv/install.sh | sh

# 환경 변수 갱신 (uv 명령어를 즉시 사용 가능하도록 설정)
source $HOME/.local/bin/env
```

### ④ 깃허브 저장소 클론 (Code Download)
작성된 최신 소스 코드를 서버로 내려받습니다.
```bash
git clone https://github.com/JuneHyeongCho/BRENXIA.git
cd BRENXIA
```

### ⑤ 환경 변수 및 설정 파일 구축 (.env)
서버에서 외부 접근이 가능하도록 설정 파일을 생성해야 합니다. 대시보드를 외부 브라우저에서 볼 수 있도록 바인딩 주소를 `0.0.0.0`으로 설정합니다.
```bash
# 설정 파일 열기 (nano 편집기 사용)
nano .env
```
편집 창이 열리면 아래 내용을 복사하여 붙여넣고 저장합니다. (저장 단축키: `Ctrl + O` 누른 후 Enter ➡️ 종료: `Ctrl + X`)
```env
# 대시보드 설정 (외부 접속 허용)
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8000

# 회사 이메일 설정
COMPANY_MASTER_EMAIL=brenxia@brenxia.com
CEO_EMAIL=psyche@brenxia.com

# 구글 서비스 계정 키 파일 경로 (기본값)
GOOGLE_CREDENTIALS_FILE=config/credentials.json
```

> [!IMPORTANT]
> **구글 서비스 계정 키 파일 업로드**
> 실제 구글 드라이브 권한 관리를 가동하려면 구글 클라우드에서 다운로드받은 서비스 계정 키 JSON 파일 내용을 복사하여 `config/credentials.json`에 붙여넣어야 합니다. (아직 준비가 안 된 경우, 파일이 없을 시 프로그램은 자동으로 안전한 시뮬레이션용 **모의 실행 모드(Mock Mode)**로 안전하게 동작합니다.)
> ```bash
> mkdir -p config
> nano config/credentials.json
> # 서비스 계정 키 JSON의 텍스트 내용을 붙여넣고 저장합니다.
> ```

### ⑥ 대시보드 서버 백그라운드 구동 (Background Run)
SSH 터미널 접속을 종료(로그아웃)하더라도 24시간 서버가 꺼지지 않도록 백그라운드로 프로세스를 가동합니다.
```bash
# 백그라운드 실행 실행 (로그는 data/dashboard.log 에 자동 누적)
mkdir -p data
nohup uv run python run_dashboard.py > data/dashboard.log 2>&1 &
```

---

## 3. 작동 상태 점검 및 종료 (Server Maintenance)

### ① 정상 동작 확인
실행 중인 서버의 동작 로그를 실시간으로 모니터링하여 오류 유무를 확인합니다.
```bash
tail -n 50 -f data/dashboard.log
```
> [!TIP]
> 로그 모니터링 화면을 빠져나오려면 `Ctrl + C`를 누르시면 됩니다.

로그 확인 중 `BRENXIA WPMS Dashboard is running!` 문구가 표시되면 성공입니다. 이제 크롬 등의 웹 브라우저를 켜고 주소창에 아래와 같이 입력하여 접속을 확인합니다.
* **대시보드 접속 주소**: `http://72.62.65.177:8000`

### ② 대시보드 서버 중단 (Stop Server)
가동 중인 서버를 종료하고 싶을 때는 아래 명령어를 터미널에 입력하여 가동 중인 파이썬 프로세스를 안전하게 종료시킵니다.
```bash
pkill -f run_dashboard.py
```
