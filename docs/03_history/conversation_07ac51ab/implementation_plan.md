# AD 에이전트 기초 구조 구현 계획 (AD Agent Initial Structure Plan)

AD(Art Director) 에이전트 개발의 첫 단계로, 기본적인 클래스 구조와 프롬프트 JSON 설정값 생성 및 임시 이미지 시안(Mock visual draft)을 생성하는 시뮬레이션 기능을 구현합니다.

## 사용자 검토 필요 (User Review Required)

> [!NOTE]
> * 이번 작업은 AD 에이전트의 기초 뼈대를 잡는 1단계 개발입니다.
> * 실제 생성형 AI API(ComfyUI / Nanobanana) 호출 대신, 파일 시스템에 더미 이미지(Mock image)를 생성하여 동작 흐름을 시뮬레이션합니다.

## 제안된 변경 사항 (Proposed Changes)

### AD 에이전트 컴포넌트 추가 (AD Agent Component)

---

#### [NEW] [ad_agent.py](file:///e:/Antigravity%20Project/vibe_cording/src/vibe_cording/ad_agent.py)
* `ADAgent` 클래스 정의:
  - `__init__(self, workspace_client=None)`: 구글 워크스페이스 클라이언트 연동 준비.
  - `generate_prompt_config(self, brief_text: str) -> dict`: 브리프 텍스트를 분석하여 ComfyUI/나노바나나 용 프롬프트 설정값(Prompt configuration - positive/negative prompts, steps, dimensions) 생성.
  - `generate_mock_visual_draft(self, prompt_config: dict, output_path: str) -> str`: 임시 이미지 파일을 생성하여 실제 이미지 시안이 생성된 것처럼 흐름을 모니터링 및 시뮬레이션.

#### [NEW] [test_ad_agent.py](file:///e:/Antigravity%20Project/vibe_cording/tests/test_ad_agent.py)
* `TestADAgent` 단위 테스트 클래스 정의:
  - 프롬프트 설정값(Prompt config)의 정합성 검증.
  - 임시 이미지 시안(Mock visual draft) 생성 및 파일 저장 기능 검증.

## 검증 계획 (Verification Plan)

### 자동화 테스트 (Automated Tests)
- 로컬 단위 테스트 실행 명령어:
  `$env:PYTHONPATH="src"; python -m unittest tests/test_ad_agent.py`
