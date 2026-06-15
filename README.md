# vibe-cording

`uv` 기반으로 구동되는 파이썬 라이브러리 프로젝트입니다.

## 개발 환경 구축 및 사용법

이 프로젝트는 패키지 관리 및 의존성 해결을 위해 [uv](https://github.com/astral-sh/uv)를 사용합니다.

### 1. 가상환경 생성 및 의존성 동기화

아래 명령어를 실행하여 가상환경(`.venv`)을 생성하고 프로젝트 의존성을 동기화합니다.
```bash
python -m uv sync
```

### 2. 코드 실행

가상환경을 실행(Activate)하지 않고도 `uv run`을 통해 패키지 내의 코드를 실행하거나 테스트 스크립트를 즉시 가동할 수 있습니다.
```bash
# 기본적으로 제공되는 hello 함수 또는 스크립트 실행 예시
python -m uv run -c "import vibe_cording; print(vibe_cording.hello())"
```

또는 가상환경을 활성화하려면 다음을 실행합니다:
* **Windows (PowerShell)**: `.venv\Scripts\Activate.ps1`
* **Windows (CMD)**: `.venv\Scripts\activate.bat`

### 3. 패키지 추가

새로운 의존성을 추가하려면 아래 명령어를 사용합니다.
```bash
# 외부 라이브러리 추가 예시 (예: requests)
python -m uv add requests

# 개발용 의존성 추가 예시 (예: pytest)
python -m uv add --dev pytest
```

### 4. 패키지 빌드

프로젝트를 배포용 배포판(wheel, sdist)으로 빌드하려면 아래 명령어를 실행합니다.
```bash
python -m uv build
```
빌드된 결과물은 `dist/` 폴더에 생성됩니다.

---

## 문서 위계 및 카탈로그 (Documentation Hierarchy & Catalog)

프로젝트와 에이전트 시스템에 관련된 모든 문서들은 다음과 같이 계층적으로 구조화되어 있습니다.

### 1. 전사 및 직능별 규칙 (Rules & Policies)
* [01_brenxia_rules.md](file:///d:/BRENXIA_Agent/docs/01_rules/01_brenxia_rules.md): BRENXIA AI 개발 및 협업 최상위 지침 규칙 문서.
* [02_pmo_rules.md](file:///d:/BRENXIA_Agent/docs/01_rules/02_pmo_rules.md): 프로젝트 관리(PMO) 절차, 구글 워크스페이스 연동 및 폴더 라이프사이클 규칙.
* [03_advertising_rules.md](file:///d:/BRENXIA_Agent/docs/01_rules/03_advertising_rules.md): 광고사업부 내 기획/제작 실무 R&R 및 11단계 광고 프로세스 지침.

### 2. 에이전트 상세 명세서 (Specifications)
* [01_pm_agent_spec.md](file:///d:/BRENXIA_Agent/docs/02_specs/01_pm_agent_spec.md): 프로젝트 매니저(PM) 에이전트 상세 설계 사양 및 동작 프로세스 명세서.
* [02_ad_agent_spec.md](file:///d:/BRENXIA_Agent/docs/02_specs/02_ad_agent_spec.md): 아트디렉터(AD) 에이전트 이미지 생성 및 ComfyUI API 연동 명세서.
* [03_vps_deployment_guide.md](file:///d:/BRENXIA_Agent/docs/02_specs/03_vps_deployment_guide.md): 호스팅어 VPS 환경에서 헤르메스 에이전트 및 대시보드를 배포/구동하는 가이드.

### 3. 히스토리 및 개발 로그 (History & Logs)
* [docs/03_history/](file:///d:/BRENXIA_Agent/docs/03_history): 이전 대화 기록 및 기능 개발 검증 보고서(Walkthrough) 보관소.

