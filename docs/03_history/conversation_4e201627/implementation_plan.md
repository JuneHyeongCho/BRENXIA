# AD 에이전트 연동 및 구축 구현 계획 (AD Agent Construction Plan)

이 계획서는 브랜드 익스피리언스 솔루션 그룹 **브렌시아(BRENXIA)**의 제작 파트 핵심 직능인 **AD 에이전트(AD Agent)**를 정교하게 구축하고, 이미지 생성 및 구글 워크스페이스 연동 자동화를 완료하기 위한 상세 개발 계획안입니다.

## User Review Required

> [!IMPORTANT]
> * **ComfyUI API 연동**: 로컬 RTX 4080 환경에서 기동 중인 ComfyUI API (`http://127.0.0.1:8188`) 호출 방식을 구현합니다. 환경 변수 `COMFYUI_API_URL`을 통해 주소를 설정할 수 있도록 처리합니다.
> * **나노바나나(Nanobanana) 연동**: `FAL_API_KEY` 환경 변수가 설정되어 있는 경우, Fal.ai API를 통해 Nanobanana 모델(또는 Flux 모델)을 활용한 신속한 이미지 시안 생성을 지원하도록 구성합니다.
> * **구글 문서 이미지 자동 삽입**: 구글 드라이브 `03.제작` 폴더에 시안 이미지를 업로드한 후, 해당 프로젝트의 기획서 구글 문서(Google Docs) 본문에 시안 이미지를 자동으로 삽입하는 기능을 구현합니다.

## Open Questions

> [!NOTE]
> 1. **기본 ComfyUI 워크플로우 JSON**: 로컬 ComfyUI에서 긍정/부정 프롬프트 노드, KSampler 노드, VAE Decode 노드 등을 파싱하기 위한 표준 노드 번호를 코드로 선언하고, 필요시 외부 JSON 템플릿 파일(`config/comfyui_workflow.json`)을 읽어올 수 있도록 처리할 예정입니다. 혹시 사용하고 계신 특정 워크플로우 노드 구조가 있다면 공유 부탁드립니다. (없을 경우 표준 텍스트-이미지 생성 기본 노드 번호 기준으로 매핑합니다.)
> 2. **기획서 구글 문서 ID**: 이미지 삽입 대상이 될 구글 문서 ID는 프로젝트 객체(`Project`)의 새로운 필드(`document_id` 또는 스프레드시트에서 동적으로 파싱된 ID)로 관리할 예정입니다.

## Proposed Changes

### 1. AD 에이전트 구현 고도화 (AD Agent Core)

---

#### [MODIFY] [ad_agent.py](file:///d:/BRENXIA_Agent/src/vibe_cording/ad_agent.py)
* `ADAgent` 클래스를 고도화하여 실제 이미지 생성 API를 호출합니다:
  - `generate_visual_draft_comfyui(self, prompt_config: dict, output_path: str) -> str`:
    - ComfyUI API(`http://127.0.0.1:8188/prompt`)에 프롬프트를 전송하여 작업을 등록합니다.
    - 웹소켓 또는 폴링 방식으로 렌더링 완료 여부를 감지합니다.
    - 생성된 이미지를 받아 로컬 `output_path`에 저장합니다.
    - 이때 실제 적용된 워크플로우 JSON 파일을 백업합니다.
  - `generate_visual_draft_nanobanana(self, prompt_config: dict, output_path: str) -> str`:
    - Fal.ai API를 호출하여 Nanobanana(또는 Schnell) 모델로 이미지를 생성하고 저장합니다.
  - `generate_visual_draft(self, prompt_config: dict, output_path: str) -> str`을 수정하여 우선순위에 따라 API를 분기 호출하도록 개정합니다:
    1. `COMFYUI_API_URL`에 ComfyUI가 기동 중인 경우 ➡️ ComfyUI 실행
    2. `FAL_API_KEY`가 환경 변수에 존재하는 경우 ➡️ Fal.ai/Nanobanana 실행
    3. `GEMINI_API_KEY`가 존재하는 경우 ➡️ Gemini Imagen 실행
    4. 모두 실패/비활성 시 ➡️ Picsum Photos 및 Mock 순차 Fallback

---

### 2. 구글 워크스페이스 연동 확장 (Google Workspace Integration)

---

#### [MODIFY] [google_workspace.py](file:///d:/BRENXIA_Agent/src/vibe_cording/google_workspace.py)
* `GoogleWorkspaceClient` 클래스에 구글 문서 이미지 삽입 API 연동을 위한 기능을 추가합니다:
  - `@property docs_service(self)`: Google Docs API (`docs/v1`) 빌더 서비스 프로퍼티 추가.
  - `insert_image_to_doc(self, document_id: str, image_url: str) -> None`:
    - Google Docs API의 `documents().batchUpdate()`를 호출하여 주어진 문서의 맨 마지막 부분 또는 지정된 위치에 `insertInlineImage` 요청을 수행합니다.
  - `upload_file_to_drive(self, folder_id: str, file_path: str, mime_type: str) -> str`:
    - 기존의 드라이브 연동에 추가하여 로컬에 생성된 시안 이미지를 드라이브의 특정 폴더(예: `03.제작`)로 직접 업로드하고 File ID와 WebContentLink를 획득하는 메서드를 구현합니다.

---

### 3. 유닛 테스트 보강 (Unit Tests)

---

#### [MODIFY] [test_ad_agent.py](file:///d:/BRENXIA_Agent/tests/test_ad_agent.py)
* ComfyUI 및 Fal.ai API 호출 시의 Mock/Stub 테스트를 보강합니다.
* 이미지 생성 성공 시 구글 드라이브 업로드 및 문서 본문 삽입 모의 함수(Mock 호출) 검증 테스트 케이스를 구축합니다.

## Verification Plan

### Automated Tests
* 로컬 가상 환경에서의 단위 테스트 실행:
  `uv run python -m unittest discover -s tests`

### Manual Verification
* `scratch/test_ad_agent_real.py`를 활용해 실제 이미지 생성, 드라이브 업로드 및 문서 본문 삽입의 전체 프로세스가 모의 환경 및 실서버 환경에서 차례대로 정상 수행되는지 로깅하여 확인합니다.
