# BRENXIA AI 에이전트 2차 협업 및 설계 논의 보고서 (Walkthrough & Design Discussion)

이 문서는 브랜드 익스피리언스 솔루션 그룹 **브렌시아(BRENXIA)**의 24/7 자율 AI 에이전트 생태계 구축을 위해 인간 실무진과 AI 에이전트가 나눈 기술 및 설계 논의 결과를 요약한 보고서입니다.

---

## 1. 인프라 구축 및 동기화 (Infrastructure & Synchronization)

### ① 로컬 Git 환경 구축 (Local Git Setup)
* **조치 사항**: Windows Package Manager(`winget`)를 활용하여 로컬 개발 환경에 **Git 2.54.0.windows.1** 버전을 성공적으로 설치 및 검증하였습니다.
* **설치 경로**: [git.exe](file:///C:/Program%20Files/Git/cmd/git.exe)

### ② GitHub 프로젝트 동기화 (Repository Sync)
* **조치 사항**: GitHub 원격 저장소(`https://github.com/JuneHyeongCho/BRENXIA.git`)를 로컬 작업 공간(`d:\BRENXIA_Agent`)에 클론(Clone)하였습니다.
* **브랜치 설정**: 이전 작업 내역과 상세 명세서가 보존되어 있는 **`master` 브랜치**로 체크아웃(Checkout)하여 동기화를 완료했습니다.

---

## 2. 24/7 헤르메스 에이전트 생태계 아이데이션 (24/7 Hermes Ecosystem Ideation)

최종 컨셉인 **"헤르메스 에이전트(Hermes Agent)를 통한 24/7 구축 가능 생태계"**를 실현하기 위해 아래와 같은 4대 핵심 가동 시나리오를 정의하였습니다.

### ① 4대 핵심 서비스 시나리오
1. **야간 자율 캠페인 기획 파이프라인 (Night-shift Autonomous Pipeline)**:
   * 인간 PM이 퇴근 전 RFP를 올리면, 밤사이 `리서처(팩트북) ➡️ AP/AE(전략 브리프) ➡️ CW/AD(시안 및 프롬프트)`가 순차적으로 자율 기동하여 아침까지 검토용 보고서 카드를 준비해 놓는 구조.
2. **에이전트 간 분쟁 해결 엔진 (AI Conflict Resolution Engine)**:
   * 카피와 비주얼 방향성에 대해 실무 AI 에이전트들 간 합의가 **3회 이상 실패할 때**, 헤르메스가 개입하여 비즈니스 목표에 부합하는 절충안(Option A, B, C)을 스스로 도출하여 제안.
3. **비동기 의사결정 및 알림 노이즈 필터링 (Asynchronous Smart Approval)**:
   * 자잘한 일상 알림은 쓰레드로 격리하고, 중대한 최종 승인 및 예산 관련 항목만 대표님(CEO) 및 담당 PM의 **1:1 다이렉트 메시지(DM) 카드**로 발송해 조작 피로도를 제거.
4. **자율 보안 및 리소스 정화 (Security & Active Resource Janitor)**:
   * 구글 챗에서 사람이 제외되면 해당 인원의 구글 드라이브 읽기/쓰기 권한을 즉시 회수하고, 48시간 방치된 임시 인프라를 자동으로 동결 보관 처리.

---

## 3. 에이전트 아키텍처 및 역할 분담 (Agent Architecture)

기존에 개발 중이던 **PM 에이전트**의 기능들을 신규 에이전트 생태계(Hermes + Paperclip) 구조에 맞춰 아래와 같이 세분화하여 이식하기로 합의했습니다.

* **목소리 (Communication) ➡️ 헤르메스 (Hermes Agent)**:
  * 구글 챗 API와 연동되어 인간 실무진과의 입출력 및 카드 발송을 전담하는 관문 역할.
* **두뇌/상태 (Orchestrator) ➡️ 페이퍼클립 (Paperclip Company OS)**:
  * 24시간 가동되는 서버 내에서 전체 워크플로우 상태, 프로젝트 목표, 칸반 보드, 에이전트 가동 비용을 제어.
* **손과 발 (Action/Tools) ➡️ 기존 PM 에이전트 (Python Core)**:
  * 폴더 생성, 권한 동기화, 스프레드시트 수치 검증 등 실제 운영 체제와 Google API를 호출하는 실행 코드로 활용.

---

## 4. 인프라 및 AI 모델 비용 최적화 설계 (Infrastructure & Cost Optimization)

### ① VPS(가상 사설 서버) 도입의 타당성
* **24/7 가동** 및 구글 챗 콜백 수신을 위한 **고정 IP/SSL 웹훅 서버** 확보를 위해 리눅스 기반의 기본 VPS(예: 월 $10~$20 선의 가벼운 클라우드 VM) 구축이 유리합니다.
* 이미지 생성을 위한 고사양 GPU는 VPS에 직접 탑재하지 않고, **서버리스 GPU API(RunPod 등)를 연결**하여 인프라 비용을 최소화합니다.

### ② AI 모델(LLM) 요금 부담 해소 방안
* **SaaS와 API의 구분**: 기존에 사용 중인 Gemini Business(SaaS)는 인간용이므로 에이전트 코드에서 호출이 불가능합니다.
* **해결책**: 에이전트 구동에 사용되는 **API는 쓴 만큼만 결제되는 종량제**이므로 비용 부담이 매우 작습니다. (100만 토큰당 약 100원 수준)
* **개발 초기 단계**: 추가 비용 결제 없이 **Google AI Studio의 무료 티어(Free Tier)**를 통해 $0원으로 모든 개발과 시뮬레이션을 진행하기로 결정했습니다.
* **OpenAI (GPT-4o) 지원**: 본 생태계는 모델 독립적으로 설계되어 설정 파일(`.env`) 수정만으로 메인 두뇌를 **GPT-4o**로 바로 변경해 기동할 수 있도록 호환성을 확보합니다.
