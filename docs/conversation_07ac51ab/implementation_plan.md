# 구글 API 속도 개선 및 최적화 구현 계획 (Google API Performance Optimization Plan)

구글 워크스페이스(Google Workspace) API 호출의 지연 시간(Latency)을 줄이고 프로그램이 멈추는 현상을 방지하기 위해 비동기 멀티스레딩(Multi-threading) 및 시트 범위 최적화(Range Optimization)를 적용합니다.

## 사용자 검토 필요 (User Review Required)

> [!NOTE]
> * 이번 개선은 내부 소스 코드(Source Code)의 로직만 최적화하므로 데이터베이스 구조나 기능 자체는 이전과 동일하게 유지됩니다.
> * 멀티스레드(Multi-thread) 방식으로 폴더 생성 및 권한 부여를 동시에 처리하므로 전체적인 속도가 약 3배~5배 이상 빨라질 것으로 예상됩니다.

## 제안된 변경 사항 (Proposed Changes)

### 구글 워크스페이스 클라이언트 최적화 (Google Workspace Client Optimization)

---

#### [MODIFY] [google_workspace.py](file:///e:/Antigravity%20Project/vibe_cording/src/vibe_cording/google_workspace.py)

1. **폴더 생성 비동기화 (Asynchronous Folder Creation)**:
   - `create_project_folders` 메서드 내에서 7개의 하위 폴더 및 각각의 아카이브 폴더 생성 작업을 `ThreadPoolExecutor`를 사용하여 병렬(Parallel)로 수행하도록 변경합니다.
2. **권한 동기화 비동기화 (Asynchronous Permission Sync)**:
   - `sync_permissions` 및 `sync_pms_permissions` 메서드 내의 사용자 이메일별 권한 추가 작업을 `ThreadPoolExecutor`로 병렬 처리하여 대기 시간을 줄입니다.
3. **수기 입력 지우기 범위 최적화 (Spreadsheet Clear Range Optimization)**:
   - `_clear_pms_manual_inputs` 메서드에서 개별 셀과 범위가 연속된 경우(예: `E79` 및 `E80:E107`) 이를 단일 범위(`E79:E107`)로 병합(Merge)하여 전체 요청 범위를 줄이고 구글 시트 API의 부담을 최소화합니다.
4. **웹훅 타임아웃 지정 (Webhook Timeout)**:
   - `send_google_chat_card` 등 `requests.post`를 사용하는 네트워크 요청에 타임아웃(`timeout=10`)을 지정하여 서버 장애 시 무한정 대기하는 프리징(Freezing) 현상을 막습니다.

## 검증 계획 (Verification Plan)

### 자동화 테스트 (Automated Tests)
- 로컬 단위 테스트 실행:
  `$env:PYTHONPATH="src"; python -m unittest tests/test_pm_agent.py`
- 실 API 연동 테스트 실행:
  `$env:PYTHONPATH="src"; python tests/test_real_api.py`

### 수동 검증 (Manual Verification)
- 구글 드라이브에 폴더들이 정상적으로 병렬 생성되는지 확인하고, 생성 속도 및 에러 로그 처리가 향상되는지 모니터링합니다.
