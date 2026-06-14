# BRENXIA 문서 위계 정비 및 폴더링 계획서 (Documentation Hierarchy Reorganization)

BRENXIA 프로젝트의 지속 가능한 확장과 협업을 위해, 산재되어 있거나 플랫(Flat)하게 위치한 마크다운(Markdown) 문서들의 위계(Hierarchy)를 바로잡고 체계적으로 분류/폴더링하는 작업을 계획합니다.

## User Review Required

> [!IMPORTANT]
> **주요 변경 내용 및 영향 범위**
> 1. **루트 파일의 이동**: 프로젝트 루트에 위치하던 최상위 규칙 문서인 [brenxia_rules.md](file:///d:/BRENXIA_Agent/brenxia_rules.md)를 `docs/01_rules/01_brenxia_rules.md`로 이동 및 이름을 변경합니다.
> 2. **명명 규칙 도입**: 파일 식별을 직관적으로 돕고 편집기 정렬 순서를 보장하기 위해 `01_`, `02_` 등의 숫자 접두사(Numerical Prefix)를 도입합니다.
> 3. **문서 상호 참조 링크 업데이트**: 규칙 문서 내부에서 서로를 링크로 가리키던 절대 경로 및 상대 경로(`file:///d:/BRENXIA_Agent/docs/...`)를 새로운 구조에 맞춰 전수 수정합니다.
> 4. **개발 코드 영향도**: 검색 결과 실제 파이썬 소스 코드나 런타임 상에서 마크다운 파일의 경로를 하드코딩하여 직접 참조하는 로직이 없어, 소스 코드 동작에 대한 영향도는 없습니다.

---

## Proposed Changes

새로운 위계 아키텍처에 맞게 폴더를 개설하고 파일을 이동/이름 변경합니다.

```
d:/BRENXIA_Agent/
├── README.md (루트 진입점 - 문서 구조 설명 추가)
└── docs/
    ├── 01_rules/ (전사 및 부서별 규칙/규정 폴더)
    │   ├── 01_brenxia_rules.md (이전 brenxia_rules.md)
    │   ├── 02_pmo_rules.md (이전 docs/pmo_rules.md)
    │   └── 03_advertising_rules.md (이전 docs/advertising_rules.md)
    │
    ├── 02_specs/ (에이전트 및 시스템 설계 상세 명세 폴더)
    │   ├── 01_pm_agent_spec.md (이전 docs/pm_agent_spec.md)
    │   └── 02_ad_agent_spec.md (이전 docs/ad_agent_spec.md)
    │
    └── 03_history/ (협업 히스토리 및 이전 대화 로그 폴더)
        ├── conversation_07ac51ab/
        └── conversation_ca645bb0/
```

---

### [Component] 1. 신규 폴더 생성 및 파일 이동 (Folder Creation & File Move)

#### [NEW] [docs/01_rules/](file:///d:/BRENXIA_Agent/docs/01_rules)
- 전사/부서 규칙을 모으기 위한 디렉토리를 생성합니다.

#### [NEW] [docs/02_specs/](file:///d:/BRENXIA_Agent/docs/02_specs)
- 에이전트 상세 명세를 모으기 위한 디렉토리를 생성합니다.

#### [NEW] [docs/03_history/](file:///d:/BRENXIA_Agent/docs/03_history)
- 역사 대화 기록 및 이력을 분류하기 위한 디렉토리를 생성합니다.

#### [DELETE] [brenxia_rules.md](file:///d:/BRENXIA_Agent/brenxia_rules.md)
- 루트의 파일을 삭제(이동)합니다.

#### [NEW] [01_brenxia_rules.md](file:///d:/BRENXIA_Agent/docs/01_rules/01_brenxia_rules.md)
- `docs/01_rules/` 아래로 이전하고 파일명을 다듬습니다.

#### [NEW] [02_pmo_rules.md](file:///d:/BRENXIA_Agent/docs/01_rules/02_pmo_rules.md)
- `docs/pmo_rules.md`를 `docs/01_rules/` 아래로 이동 및 이름을 변경합니다.

#### [NEW] [03_advertising_rules.md](file:///d:/BRENXIA_Agent/docs/01_rules/03_advertising_rules.md)
- `docs/advertising_rules.md`를 `docs/01_rules/` 아래로 이동 및 이름을 변경합니다.

#### [NEW] [01_pm_agent_spec.md](file:///d:/BRENXIA_Agent/docs/02_specs/01_pm_agent_spec.md)
- `docs/pm_agent_spec.md`를 `docs/02_specs/` 아래로 이동 및 이름을 변경합니다.

#### [NEW] [02_ad_agent_spec.md](file:///d:/BRENXIA_Agent/docs/02_specs/02_ad_agent_spec.md)
- `docs/ad_agent_spec.md` to `docs/02_specs/` 아래로 이동 및 이름을 변경합니다.

#### [NEW] [03_history/conversation_07ac51ab/](file:///d:/BRENXIA_Agent/docs/03_history/conversation_07ac51ab)
- `docs/conversation_07ac51ab` 폴더를 `docs/03_history` 아래로 이동합니다.

#### [NEW] [03_history/conversation_ca645bb0/](file:///d:/BRENXIA_Agent/docs/03_history/conversation_ca645bb0)
- `docs/conversation_ca645bb0` 폴더를 `docs/03_history` 아래로 이동합니다.

---

### [Component] 2. 내부 상호 참조 링크 갱신 (Documentation Links Update)

#### [MODIFY] [01_brenxia_rules.md](file:///d:/BRENXIA_Agent/docs/01_rules/01_brenxia_rules.md)
- 내부에 기재된 `PMO 직능 부문` 및 `광고사업부 직능 부문` 마크다운 파일 링크를 갱신합니다.
- 변경 전:
  ```markdown
  * **PMO 직능 부문**: [docs/pmo_rules.md](file:///d:/BRENXIA_Agent/docs/pmo_rules.md)
  ...
  * **광고사업부 직능 부문**: [docs/advertising_rules.md](file:///d:/BRENXIA_Agent/docs/advertising_rules.md)
  ```
- 변경 후:
  ```markdown
  * **PMO 직능 부문**: [docs/01_rules/02_pmo_rules.md](file:///d:/BRENXIA_Agent/docs/01_rules/02_pmo_rules.md)
  ...
  * **광고사업부 직능 부문**: [docs/01_rules/03_advertising_rules.md](file:///d:/BRENXIA_Agent/docs/01_rules/03_advertising_rules.md)
  ```

#### [MODIFY] [README.md](file:///d:/BRENXIA_Agent/README.md)
- 프로젝트 최상위 진입점인 README 하단에 이번에 정리된 문서 위계 설명 및 링크 목록(Documentation Catalog)을 명시적으로 수록하여 한눈에 파악할 수 있도록 돕습니다.

---

## Verification Plan

### Manual Verification
- 파일 이동 후 로컬 git status를 통해 모든 이동 내역이 추적되는지 확인합니다.
- 변경된 파일들을 열어 상호 참조 링크(마크다운 내 클릭 가능한 절대/상대 경로)가 깨지지 않고 의도한 새 위치를 가리키는지 확인합니다.
- 전체 단위 테스트(`uv run pytest`)를 구동하여 문서 이동이 파이썬 테스트 실행에 전혀 지장을 주지 않음을 재입증합니다.
