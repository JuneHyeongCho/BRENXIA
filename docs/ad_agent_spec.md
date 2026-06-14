# BRENXIA AD 에이전트 상세 명세서 (AD Agent Specifications)

이 문서는 브랜드 익스피리언스 솔루션 그룹 **브렌시아(BRENXIA)**의 크리에이티브 시안 및 이미지 생성을 담당하는 **AD 에이전트(AD Agent / Art Director)**의 설계 사양서입니다.

---

## 1. 개요 및 역할 (Overview & Role)
* **목적**: 기획안(Creative Brief) 및 CD의 방향성에 부합하는 광고 캠페인의 비주얼 시안(Visual Draft)을 생성하고 제안하는 역할을 담당합니다.
* **통합 엔진**: 이미지 생성형 AI(Generative AI) 엔진인 **ComfyUI** 및 **나노바나나(Nanobanana) API**와의 연동을 관리합니다.
* **협업 프로세스**: 디렉터와 디자이너의 사전 승인을 거쳐 최종적으로 도출된 고품질 비주얼 시안을 구글 드라이브의 지정된 폴더에 저장하고 기획서 문서에 자동 추가합니다.

---

## 2. 입출력 스펙 (Input & Output Specifications)

### ① 입력 데이터 (Input)
* **크리에이티브 브리프 (Creative Brief)**: 캠페인의 목표, 타깃 소비자, 핵심 메시지 등을 포함한 텍스트 데이터.
* **CD 디렉션 (CD Direction)**: CD가 제시한 핵심 비주얼 테마 및 브랜드 톤앤매너(Tone & Manner).

### ② 산출 데이터 (Output)
* **프롬프트 설정값 (Prompt Configuration - JSON)**:
  - `positive_prompt`: 긍정 프롬프트 (예: 고품질 스타일, 조명, 구도 등)
  - `negative_prompt`: 부정 프롬프트 (예: 저품질 요소, 찌그러진 형태 방지 등)
  - `dimensions`: 생성 이미지 크기 (width, height)
  - `parameters`: 생성 옵션 (steps, cfg_scale, sampler_name)
* **비주얼 시안 (Visual Draft - PNG/JPG)**: 실제 생성 완료된 고화질 이미지 파일.
* **워크플로우 아카이브 (Workflow Archive - JSON)**: 이미지 생성 시점에 실제 사용된 ComfyUI API 포맷의 워크플로우 그래프 구조 및 설정값 백업 파일.

---

## 3. 핵심 동작 흐름 (Core Workflow)

```mermaid
graph TD
    Brief[크리에이티브 브리프 수신] --> Analyze[브리프 텍스트 분석 및 프롬프트 추출]
    Analyze --> Config[Prompt JSON 설정값 생성]
    Config --> Chat[구글 챗 스페이스에 [승인 요청] 카드 발송]
    Chat --> Approval{인간 디렉터의 승인?}
    Approval -->|Approved 승인| CallAPI[로컬 RTX 4080 ComfyUI API 호출]
    Approval -->|Rejected 반려| Modify[프롬프트 수정 및 재기안]
    CallAPI --> Save[구글 드라이브 03.제작 폴더 저장]
    Save --> Insert[기획서 구글 문서에 이미지 자동 삽입]
```

1. **프롬프트 구성 단계**: 기획 텍스트를 파싱하여 감정적 깊이와 시각적 요소가 강조된 긍정/부정 프롬프트 구조(JSON)를 조립합니다.
2. **사전 승인 단계**: 비용 및 리소스 낭비를 방지하기 위해 생성 API 호출 전, 구글 챗에 프롬프트 구성 카드를 노출하여 승인을 요청합니다.
3. **API 연동 및 배포 단계**: 
   * **로컬 RTX 4080 인프라 가동**: 로컬 PC(RTX 4080 GPU, VRAM 16GB) 환경에서 구동되는 ComfyUI API 엔드포인트(`http://127.0.0.1:8188`)를 호출하여 실시간 렌더링을 실행합니다.
   * **자산 및 워크플로우 아카이빙**: 생성 완료된 이미지 파일명과 매핑하여 해당 이미지 생성에 실제로 적용된 **ComfyUI API Workflow JSON** 파일을 구글 드라이브의 `03.제작/_이전버전_아카이브` 폴더 및 DB에 함께 저장(Archive)합니다.
   * **지속적 학습 데이터 자산화 (LoRA Fine-tuning Prep)**: 아카이빙된 `[이미지 + 프롬프트 텍스트 + 워크플로우 JSON]` 세트를 고유 자산 폴더에 누적하여, 추후 특정 브랜드 톤앤매너(예: 마스터카드/우리카드 전용 스타일) 학습(LoRA Fine-tuning) 시의 트레이닝 데이터셋(Training Dataset)으로 즉시 활용할 수 있도록 정렬 보관합니다.

---

## 4. 아키텍처 및 구현 설계 (Implementation Class)

AD 에이전트는 [ad_agent.py](file:///e:/Antigravity Project/vibe_cording/src/vibe_cording/ad_agent.py) 파일에 구현되며, 초기 시뮬레이션 버전은 더미 이미지 파일을 파일 시스템에 생성하는 방식으로 동작합니다.

```python
# System Structure Reference (Non-korean code layout)
class ADAgent:
    def __init__(self, workspace_client=None):
        self.workspace = workspace_client

    def generate_prompt_config(self, brief_text: str) -> dict:
        """
        Parses creative brief and generates optimal prompt JSON structure.
        """
        # Parse logic to extract visual styles
        return {
            "positive_prompt": "premium brand campaign visual, cinematic lighting, 8k resolution",
            "negative_prompt": "ugly, blurry, low quality, distorted",
            "width": 1024,
            "height": 1024,
            "steps": 30,
            "cfg_scale": 7.5
        }

    def generate_mock_visual_draft(self, prompt_config: dict, output_path: str) -> str:
        """
        Simulates image generation API call by writing a mock file to disk.
        """
        # Create a mock file to represent generated visual
        with open(output_path, "wb") as f:
            f.write(b"MOCK_IMAGE_DATA")
        return output_path
```
