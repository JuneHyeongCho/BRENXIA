# BRENXIA AI 개발 및 협업 규칙 (BRENXIA AI Rules)

이 문서는 브랜드 익스피리언스 솔루션 그룹 **브렌시아(BRENXIA)**의 AI 에이전트 개발과 AI 협업을 위한 최상위 지침입니다. 코딩을 하지 않는 최종의사결정자(CEO)와 AI 코딩 어시스턴트가 프로젝트를 안정적이고 생산적으로 이끌어갈 수 있도록 돕습니다.

---

## 1. 역할 명칭 및 정의 (Role Definitions)

본 문서와 시스템 내부에서 사용되는 사용자 및 에이전트의 역할 명칭을 다음과 같이 통일하여 정의합니다.

* **최종의사결정자 (CEO)**: 에이전시의 대표이사로, 회사 전체의 중요 프로젝트 및 전략의 최종 승인권자입니다.
* **프로젝트 관리자 (Admin)**: 프로젝트의 개설 여부와 열람 권한 범위를 결정하는 승인권자입니다. 창업 초기 단계에서는 최종의사결정자(CEO)가 프로젝트 관리자(Admin) 권한을 겸임할 수 있으나, 시스템 확장 및 보안 관리를 위해 향후 프로젝트 관리자(Admin) 계정은 반드시 별도의 권한과 계정으로 분리되어 운영되어야 합니다.
* **휴먼 담당 PM (Human Lead PM)**: 실제 프로젝트의 일상적인 진행과 전체 실무 책임을 전담하고 최종 의사결정을 내리는 **사람(인간) 기획자**입니다. 일반 프로젝트의 최종 승인 권한을 가집니다.
* **헤르메스 에이전트 (Hermes Agent / CEO Agent)**: 구글 챗 스페이스 관리, 드라이브 아카이빙, WBS 관리 등 프로세스를 자동 보좌하고 지휘하는 **최고경영 AI 에이전트**입니다.

### ① 시스템 구성 계정 맵 (System Account Mapping)

본 시스템은 **회사 공식 시스템 구축**을 목표로 개발되나, 비용 집행 및 테스트 편의성을 고려하여 **사용자 개인 계정을 테스트용 샌드박스(Sandbox) 환경으로 활용**합니다. 모든 코드는 향후 회사 계정으로 쉽게 전환할 수 있도록 환경 변수(Environment Variables)를 통해 설정 가능하도록 설계해야 합니다.

* **사용자 개인 계정 (User Personal Account - 테스트/샌드박스 환경)**: `adpeople0310@gmail.com`
  - **용도**: 실제 비용 집행을 방지하고 안전하게 검증하기 위한 **개발 및 테스트(Test)용 계정**
  - **대상 서비스**: 안티그래비티(Antigravity), 호스팅어 & VPS(Hostinger & VPS), 챗GPT(ChatGPT), 테스트용 구글 계정, 피그마(Figma), 컴피유아이(ComfyUI)
* **사용자 회사 계정 (User Company Account - 향후 운영 환경)**:
  - **최고 관리자 마스터 계정 (Super Admin / Master)**: `brenxia@brenxia.com`
    - **용도**: 구글 워크스페이스 최고 관리자 콘솔 및 전사 인프라 제어용
    - **규칙**: 생태계 구축 단계에서 회사 계정을 활용하는 경우, 관리자 콘솔 및 API 제어 권한 조작이 필수적이므로 모든 인프라 셋업 및 설정 작업은 반드시 **`brenxia@brenxia.com`** 계정으로 수행하거나 해당 계정에 작업을 요청해야 합니다.
  - **프로젝트 관리자 계정 (Admin)**: `psyche@brenxia.com` (실제 운영 단계의 개별 프로젝트 승인 및 실무 모니터링용)

---

## 2. 기본 소통 규칙 (Bilingual & Plain Language Rules)

* **한국어 우선 대응 (Korean First)**: 모든 설명, 안내, 피드백은 한국어를 기본으로 작성합니다.
* **이중 표기 정책 (Bilingual Notation)**: IT 기술 용어, 마케팅 전문 용어, 개발 개념을 사용할 때는 반드시 영어 표기를 괄호 안에 병기합니다.
  - *예시: "사용자 인터페이스(UI), 프로젝트 관리(PMO), 가상환경(Virtual Environment)"*
* **중학생 수준의 쉬운 설명 (Plain Explanations)**: 복잡한 프로그래밍 언어나 아키텍처 이론은 피하고, 비개발자인 최종의사결정자(CEO)와 휴먼 담당 PM(Human Lead PM)이 즉시 이해할 수 있는 쉬운 어휘로 설명합니다. 전문 용어가 불가피할 경우 먼저 쉽게 풀어서 설명합니다.

---

## 3. 비개발자(Non-coder) 맞춤형 개발 지침 (No-Code Friendly Guidelines)

* **코드 플레이스홀더 금지 (No Placeholders)**: 코드를 제공할 때 `// 여기에 코드를 작성하세요` 같은 생략 표기를 절대 사용하지 않습니다. 복사하여 즉시 실행 가능한 **완성형 코드**만 제공합니다.
* **복사-붙여넣기 가이드라인 (Copy-Paste Deployment)**: 개발 환경 구축 및 실행 시, 터미널에 복사해서 바로 붙여넣을 수 있는 원라인(One-line) 명령어 또는 영어 주석이 포함된 실행 파일을 제공합니다.
* **코드 내 한글 입력 금지 (No Korean in Code)**: 한글 인코딩(Encoding) 오류를 방지하기 위해 실제 소스 코드(Source Code), 주석(Comments), 변수명(Variable names), 함수명(Function names), 문자열(String literals) 등 코드 파일 내부의 모든 입력은 반드시 영어(English)로만 작성합니다. 단, 사용자 화면 UI나 터미널 출력 등 최종 사용자(User)용 설명은 한국어를 허용합니다.
* **친절하고 명확한 경로 표시**: 수정할 파일이나 실행할 경로를 알려줄 때는 클릭 가능한 마크다운 링크와 정확한 절대 경로를 사용합니다.

---

## 4. 브렌시아 비즈니스 및 도메인 지식 (BRENXIA Domain Knowledge)

* **브렌시아 철학**: 모든 산출물과 브리프는 브렌시아의 핵심 철학인 **"본질에서 출발한 경험(Experience from Essence)"**을 내포해야 합니다. 타깃 소비자의 감정적 깊이와 브랜드의 고유함을 전략에 반영합니다.
* **협업 인프라**:
  - **메인 플랫폼**: 구글 워크스페이스(Google Workspace) - 문서(Docs), 스프레드시트(Sheets), 드라이브(Drive), 구글 챗(Google Chat)
  - **제작 및 디자인**: 피그마(Figma), 컴피유아이(ComfyUI) API 연동, 어도비 CC(Adobe CC)
  - **문서 표준**: 마이크로소프트 오피스 365(Microsoft Office 365)

---

## 5. BRENXIA 멀티 에이전트 시스템 아키텍처 (Multi-Agent Blueprint)

점진적인 전사 에이전트 개발 및 확장을 위해, 회사의 전체 에이전트 시스템은 **페이퍼클립(Paperclip - Company OS Framework)**의 조직도(Org Chart) 구조 하에 **헤르메스(Hermes Agent - CEO)**를 정점으로 하여 구성됩니다.

```mermaid
graph TD
    %% 사용자 및 결재선 노드 구성
    LeadPM([휴먼 담당 PM: Human Lead PM]) <--> CEO[CEO: 헤르메스 에이전트 (Hermes Agent)]
    Admin([프로젝트 관리자: Admin]) <--> CEO
    
    %% 부서장 (C-level / Directors)
    subgraph 부서장 파트 (Directors)
        PD[PD: 플래닝 디렉터 에이전트]
        CD[CD: 크리에이티브 디렉터 에이전트]
    end
    
    %% 기획 파트
    subgraph 기획 파트 (Planning - Sub-agents)
        Researcher[전문 리서처 에이전트] -->|팩트북| AP_AE[AP / AE 에이전트]
        AP_AE -->|전략 브리프| PD
    end

    %% 제작 파트
    subgraph 제작 파트 (Creative - Sub-agents)
        CD -->|크리에이티브 컨셉| CW[CW: 카피라이터 에이전트]
        CD -->|비주얼 디렉션| AD[AD: 아트디렉터 에이전트]
        CW -->|카피 시안| Designer[UI/UX 디자이너 에이전트]
        AD -->|비주얼 시안| Designer
    end
    
    %% 미디어 파트
    subgraph 미디어 파트 (Media)
        Media[미디어 에이전트]
    end

    %% 프로세스 연동 관계
    CEO <-->|목표 부여 및 조율| PD
    CEO <-->|목표 부여 및 조율| CD
    CEO <-->|의견 요약 수신| Media
    PD -->|크리에이티브 브리프 제공| CD
    PD <-->|1차 검토| LeadPM
    CD <-->|1차 검토| LeadPM
```

### ① 헤르메스-페이퍼클립 에이전트 동기화 아키텍처 (Hermes-Paperclip Sync Architecture)
헤르메스(Hermes Agent)와 페이퍼클립(Paperclip Company OS)은 가상 직원에 대한 정보를 별도로 관리하지 않으며, 아래의 방식을 통해 **단일 에이전트 엔티티(Single Agent Entity)**를 공유하고 유기적으로 동기화(Synchronization)합니다.

* **데이터베이스 공유(Shared Database)**: 페이퍼클립이 관리하는 에이전트 목록(이름, 역할, 예산, 상태) 데이터베이스(Database)에 헤르메스도 실시간으로 접근하여 데이터를 조회하고 수정합니다.
* **통합 에이전트 API(Unified Agent API)**: 실무 에이전트(리서처, 기획, 제작 등)의 실제 비즈니스 로직(Business Logic)은 독립된 단일 웹 서비스 API 형태로 실행되며, 헤르메스(구글 챗 명령)와 페이퍼클립(스케줄러/칸반 흐름) 양측 모두 이 공통 API를 호출(Call)하여 작업을 지시합니다.

### ② 직능 부문별 세부 규칙 문서 링크 (Job Function Rules Links)
사내 직능별 세부 R&R 및 상세 작동 프로세스는 아래 분리된 문서를 참조하십시오.

* **PMO 직능 부문**: [02_pmo_rules.md](file:///d:/BRENXIA_Agent/docs/01_rules/02_pmo_rules.md)
  - 프로젝트 관리, 구글 드라이브 폴더 명명 및 인프라 구축 규칙
  - PMS 스프레드시트 수식 연동 및 데이터 누락 점검 규칙
  - 버전 관리(Version Push-down) 및 아카이빙(Archiving) 지침
  - 프로젝트 완료에 따른 접근 권한 차단 및 하이브리드 파일 잠금 규칙
* **광고사업부 직능 부문**: [03_advertising_rules.md](file:///d:/BRENXIA_Agent/docs/01_rules/03_advertising_rules.md)
  - 기획(Researcher, AP/AE, PD) 및 제작(CD, CW, AD, Designer) 세부 R&R
  - 11단계 광고 프로세스 지침 (11-Step Advertising Process Rules)
  - 인간 주도 작업물의 AI 검토 생략 규칙 (Human Bypass Rule)
  - 기획/제작 리뷰 교착 시 직능 책임자 의사결정 우선 부여 규칙
  - 광고주 피드백에 따른 역방향 프로세스 라우팅(Reverse Routing) 규칙

---

## 6. 하이브리드 에이전트 자동 확장 프로토콜 (Hybrid Agent Expansion Protocol)

프로젝트 기획서/RFP 분석 과정에서 필요한 역할의 에이전트가 브렌시아 시스템 내에 부재할 경우, 헤르메스 에이전트는 다음과 같은 하이브리드 확장 프로세스를 실행합니다.

### ① 공백 역할 감지 및 생성 제안
1. **공백 감지**: 헤르메스 에이전트가 프로젝트 과업 요구사항을 분석하여 기존 에이전트(AP, AE, CW, AD, Designer)가 커버할 수 없는 새로운 전문적 과업이 있는 경우 공백을 감지합니다.
2. **구글 챗 제안 카드 발송**: 구글 챗 스페이스에 **[신규 에이전트 생성 제안 카드]**를 발송하고 세 가지 해결 옵션을 제안합니다.

### ② 확장 옵션의 선택 및 처리
1. **옵션 A: AI 에이전트 즉시 자동 생성 (Auto-Generation)**
   - 단순 텍스트 번역, 표준 문서 검수 등 일반 LLM 프롬프트 수준에서 대응 가능한 에이전트의 경우에 적용합니다.
   - **정적 템플릿 바인딩 (Static Instance Binding) 규칙**: 에이전트를 매번 새로 코딩하여 동적으로 생성·기동하는 방식을 전면 배제합니다. 시스템 내부에 기성 정의된 **페르소나 기본 템플릿(Template) 데이터베이스**를 사전에 구축해 두고, 새로운 에이전트 배포 시 해당 기본 인스턴스에 대상 프로젝트의 매개변수(Parameter)와 전용 시스템 프롬프트(System Prompt)만 유연하게 갈아끼우는 방식으로 정적 바인딩(Binding)하여 안전하게 즉시 활성화합니다.
2. **옵션 B: 외부 솔루션/API 연동 (External Integration)**
   - 영상 자동 생성, 고도화된 통계 분석, 특정 서드파티 툴 등 외부의 기성 AI 모델이나 API 키를 필요로 하는 특수 에이전트의 경우에 적용합니다.
   - 에이전트가 필요한 외부 플랫폼(API)을 추천하고, 사용자가 API 키를 입력하면 시스템에 해당 에이전트를 조립(연동)하여 활성화합니다.
3. **옵션 C: 신규 에이전트 개발 명세서 발행 (Developer Request)**
   - 프레임워크 설계가 필요하거나 복잡한 커스텀 로직을 코딩해야 하는 경우에 적용합니다.
   - 에이전트가 기술적 요구 사양을 담은 **[에이전트 개발 명세서]**를 구글 문서로 자동 발행합니다. 최종의사결정자(CEO) 또는 휴먼 개발 담당자는 이를 개발자나 AI 코딩 파트너에게 전달해 구현을 요청합니다.
