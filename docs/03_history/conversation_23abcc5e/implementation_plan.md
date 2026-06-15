# BRENXIA 멀티 에이전트 시스템 VPS 배포 및 연동 계획서 (BRENXIA Deployment & Sync Plan)

이 계획서는 호스팅어(Hostinger) 가상 사설 서버(VPS) 환경에 헤르메스 에이전트(Hermes Agent - CEO), 페이퍼클립 OS(Paperclip OS - Company OS), 그리고 BRENXIA PM 에이전트(Python Backend)를 배포하고 상호 연동하기 위한 절차를 정의합니다.

---

## User Review Required (사용자 검토 필요 사항)

가상 서버(VPS) 호스트 컴퓨터(`72.62.65.177`)를 제어하고 코드를 배포하려면, 로컬 PC에서 VPS로의 안전한 **SSH 접속 권한**이 필요합니다. 아래 두 가지 옵션 중 편하신 방안을 선택해 주세요.

> [!IMPORTANT]
> **SSH 접속 권한 획득을 위한 두 가지 옵션:**
> * **옵션 1 (권장): SSH 키 등록**
>   - 로컬 PC에서 SSH 키(공개키/비공개키 쌍)를 생성한 후, 공개키를 VPS의 `/root/.ssh/authorized_keys`에 등록하거나 호스팅어 제어판에 등록합니다. 이후 암호 없이 안전하게 접속할 수 있습니다.
> * **옵션 2: VPS 루트(root) 비밀번호 제공**
>   - VPS의 `root` 계정 비밀번호를 제공해 주시면, 로컬 PC에서 자동으로 SSH 접속 연결을 구성하겠습니다. (비밀번호는 외부로 유출되지 않으며 세션 종료 시점까지만 일시적으로 사용됩니다.)

---

## Open Questions (확인 및 질문 사항)

1. **GCP 서비스 계정 키 파일 (GCP Service Account Key):**
   - 구글 챗 API 연동 및 구글 드라이브 관리를 위해 GCP 서비스 계정 키 파일(`credentials.json`)이 필요합니다. 이 키는 현재 로컬 PC의 [config](file:///d:/BRENXIA_Agent/config) 폴더 또는 특정 위치에 저장되어 있나요?
2. **호스팅어 가상 서버(VPS) 환경 상태:**
   - 현재 가상 서버 웹 터미널의 프롬프트가 `root@292ba4a43b0eb:/opt/hermes#`로 표시되는 것으로 보아, 호스팅어의 Docker 템플릿 환경을 사용 중이며 웹 터미널은 컨테이너 내부에 접속되어 있는 상태입니다. 
   - 혹시 VPS 호스트 자체의 `root` 비밀번호를 알고 계시거나, 호스팅어 제어판의 'SSH 키(SSH Keys)' 메뉴에 로컬 PC의 SSH 키를 등록하실 수 있나요?

---

## Proposed Changes (배포 및 구성 단계)

### Phase 1: 로컬 PC SSH 키 생성 및 가상 서버(VPS) 연동

#### [NEW] [C:\Users\menta\.ssh\id_ed25519](file:///C:/Users/menta/.ssh/id_ed25519) (SSH Private Key)
#### [NEW] [C:\Users\menta\.ssh\id_ed25519.pub](file:///C:/Users/menta/.ssh/id_ed25519.pub) (SSH Public Key)
* 로컬 PC에서 가상 서버로 안전하게 로그인하기 위해 SSH 키 쌍을 생성합니다.
* 생성된 공개키(`id_ed25519.pub`)의 텍스트 내용을 확인하여 사용자에게 공유하고, 이를 VPS 서버에 등록하도록 안내하거나 비밀번호를 통해 자동 주입합니다.

### Phase 2: 헤르메스 에이전트 컨테이너 내부 진단 및 자동 수정 (`hermes doctor --fix`)

* SSH를 통해 VPS 컨테이너 내부로 접속하거나 명령어 스크립트를 전달하여 아래 작업을 수행합니다.
  1. `hermes doctor --fix` 명령어를 실행하여 심링크(`~/.local/bin/hermes` 등) 누락 문제를 자동 해결합니다.
  2. `hermes gateway` 백그라운드 구동을 활성화하여 구글 챗 메시지 수신 대기 상태로 만듭니다.

### Phase 3: BRENXIA 파이썬 백엔드 (PM Agent) 배포

* VPS 호스트 서버에 접속하여 깃(Git)을 설치하고 저장소를 클론합니다:
  ```bash
  sudo apt-get update && sudo apt-get install -y git
  git clone https://github.com/JuneHyeongCho/BRENXIA.git /root/BRENXIA
  ```
* [config](file:///d:/BRENXIA_Agent/config) 폴더 아래에 `credentials.json` (GCP 서비스 계정 키) 파일을 생성 및 주입합니다.
* 가상 서버의 `/root/BRENXIA/.env` 환경 설정 파일을 생성합니다:
  ```env
  DASHBOARD_HOST=0.0.0.0
  DASHBOARD_PORT=8000
  COMPANY_MASTER_EMAIL=brenxia@brenxia.com
  CEO_EMAIL=psyche@brenxia.com
  SHARED_DRIVE_ROOT_ID=root
  GOOGLE_CREDENTIALS_FILE=config/credentials.json
  ```
* Docker Compose를 활용하여 PM 에이전트 백엔드 컨테이너를 빌드 및 가동합니다:
  ```bash
  cd /root/BRENXIA
  docker compose up -d --build
  ```

---

## Verification Plan (검증 계획)

### 수동 검증 (Manual Verification)
1. **네트워크 및 대시보드 접속 확인:**
   - 인터넷 브라우저에서 `http://72.62.65.177:8000`으로 접속하여 페이퍼클립 OS 대시보드 화면이 정상적으로 출력되는지 확인합니다.
2. **구글 챗 봇 연동 테스트:**
   - 구글 챗 스페이스(Space) 또는 1:1 대화방에 `BRENXIA_Hermes` 봇을 초대합니다.
   - `"안녕 헤르메스"` 혹은 `"프로젝트 현황 보여줘"` 등의 테스트 메시지를 전송하고, Pub/Sub을 거쳐 서버가 메시지를 정상적으로 수신하고 회신하는지 로그를 점검합니다.
