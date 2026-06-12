# BRENXIA PM 에이전트 상세 명세서 (PM Agent Specifications)

이 문서는 브랜드 익스피리언스 솔루션 그룹 **브렌시아(BRENXIA)**의 프로젝트 관리 자동화 시스템을 담당하는 **PM 에이전트(PM Agent)**의 아키텍처 및 세부 기능 동작 규칙을 정의한 설계 사양서입니다.

---

## 1. 개요 및 역할 (Overview & Role)
* **목적**: 기획, 제작, 미디어 등 다양한 하부 직능 에이전트들과 인간 실무진을 유기적으로 조율하는 오케스트레이터(Orchestrator) 역할을 수행합니다.
* **주요 소통 채널**: 구글 챗(Google Chat) 스페이스를 기반으로 카드를 발송하여 인터랙티브한 소통(Interactive Communication)을 보좌합니다.
* **데이터 관리**: 내부 데이터베이스(Database) 및 광고주별 PMS 구글 스프레드시트(Spreadsheet)를 동기화하여 프로젝트의 생애주기(Lifecycle)를 관리합니다.

---

## 2. 프로젝트 관리 생애주기 (Project Lifecycle Flow)

### ① 착수 및 킥오프 단계 (Initiation & Kick-off)
1. **일반 등급 (Standard Project)**: 
   - 휴먼 담당 PM(Lead PM)의 요청 시 별도의 승인 없이 즉시 구글 드라이브 및 구글 챗 채널 인프라를 자동 배포합니다.
   - *리소스 클린업(Resource Clean-up)*: 개설 후 48시간 내에 산출물이 업로드되지 않으면 자동 보관 처리합니다.
2. **중요 등급 (Critical Project)**:
   - PM 에이전트가 관리자(Admin)에게 승인 요청 카드를 보내고, 승인 버튼 클릭 시에만 배포를 실행합니다.
   - *필수 승인 정보*: 광고주명, 브랜드명, 프로젝트명, 담당 PM, 프로젝트 중요 등급, 참여 실무진 목록.
3. **책임자 검증 규칙 (Responsible Director Verification)**:
   - 기획/운영 책임자(PD)와 제작 책임자(CD)의 정보가 지정되어 있는지 반드시 검증하며, 누락 시 인프라 개설을 홀딩(Hold)합니다.

### ② 드라이브 인프라 자동 개설 (Folder Hierarchy)
프로젝트 개설 즉시 공유 드라이브의 연도별 폴더 아래에 `[YYMMDD]_[광고주_브랜드_프로젝트명]` 포맷의 루트 폴더를 만들고 7대 표준 하위 폴더를 자동 생성합니다.
* `00.고객사 제공자료` (RFP, 기초 데이터 보관)
* `01.제안` (제안서 보관)
* `02.기획` (전략 브리프 등 기획 문서 보관)
* `03.제작` (카피라이팅 시안, 비주얼 이미지 시안 보관)
* `04.미디어` (미디어 효율 의견서 등 보관)
* `05.행정` (계약서 및 정산 서류 보관)
* `06.PMS` (광고주별 PMS 관리 시트 보관)

---

## 3. 핵심 자동화 기능 (Core Automation Functions)

### ① 자동 버전 관리 및 아카이빙 (Auto Version Control)
* 각 표준 폴더(00~06) 아래에 `_이전버전_아카이브` 폴더를 자동 생성합니다.
* 최상위 폴더에는 항상 단 하나의 최신(최종) 버전 파일만 유지하고, 신버전 업로드 시 기존 구버전 파일은 아카이브 폴더로 자동 이동(Version Push-down)시킵니다.
* 파일명에 `*_최종_*` 또는 `*_V1.0_*` 패턴 매칭 시, WBS 업무 상태를 '검토 대기(Review Pending)'로 업데이트할지 묻는 컨펌 카드를 구글 챗에 자동 발송합니다.

### ② 권한 자동 동기화 (Space-to-Drive Sync)
* 구글 챗 스페이스(Space)에 새로운 실무자가 초대되거나 제외될 경우, PM 에이전트가 이를 실시간 감지하여 구글 드라이브 프로젝트 폴더의 읽기/쓰기 권한(Access Rights)을 자동으로 동기화합니다.
* 외부 파트너가 구글 챗에 참여하는 경우, 보안 강화를 위해 `05.행정` 및 `04.미디어` 폴더를 제외한 일반 폴더에만 쓰기 권한을 임시 유예 부여합니다.

### ③ PMS 구글 스프레드시트 연동 (PMS Integration)
* 광고주 단위로 단 하나의 관리 시트(`BRENXIA WPMS_[광고주명].gsheet`)를 유지하며, 신규 프로젝트는 새 행(Row)으로 추가합니다.
* **빈 칸 검증 원칙 (Null-only Validation)**: 
   - 매월 정산 및 프로젝트 상태 변경 시 매출/매입 금액과 투입 공수(M/M)를 점검합니다.
   - 숫자 **`0`**이 명시적으로 입력된 경우는 정상 수치로 판단하며, **값이 완전히 비어 있는 빈 칸(Null)**인 경우에만 누락 알림 카드를 구글 챗으로 발송하고 링크를 제공합니다.

### ④ 하이브리드 파일 잠금 (Hybrid Lock Rules)
* 프로젝트 완료(Closure) 시 모든 드라이브 폴더의 접근 권한을 읽기 전용(Read-only)으로 즉시 잠급니다.
* 단, 세금계산서 발행 및 최종 정산이 빈번한 `05.행정` 폴더에 대해서는 휴먼 PM이 구글 챗에서 **[정산 잠금 승인]**을 누를 때까지 쓰기 권한 잠금을 임시 보류(Deferred Lock)합니다.

---

## 4. 아키텍처 및 구현 설계 (Implementation & Properties)

PM 에이전트는 [pm_agent.py](file:///e:/Antigravity Project/vibe_cording/src/vibe_cording/pm_agent.py) 파일에 구현되어 있으며, 비동기 및 스레드 세이프(Thread-safe)하게 최적화된 구글 워크스페이스 클라이언트를 활용합니다.

```python
# System Structure Reference (Non-korean code layout)
class PMAgent:
    def __init__(self, db_path: str, is_mock: Optional[bool] = None):
        self.config = Config()
        self.db = LocalJSONDatabase(db_path)
        self.workspace = GoogleWorkspaceClient(
            credentials_path=self.config.GOOGLE_CREDENTIALS_FILE,
            is_mock=is_mock
        )
        self.dashboard_server = DashboardServer(db=self.db)
```
