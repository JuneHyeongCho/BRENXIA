# BRENXIA 지식 자동화 파이프라인 (Knowledge-as-Code)

이 문서는 향후 BRENXIA 에이전트(헤르메스, 아트 디렉터, 카피라이터 등)의 지능을 고도화하고 학습 데이터를 체계적으로 관리하기 위한 **[Obsidian ➡️ GitHub ➡️ VPS 자동 학습 파이프라인]** 구축 아젠다입니다.

## 1. 아키텍처 개요 (Architecture Overview)
기존의 페이퍼클립 UI나 VPS 수동 업로드 방식을 탈피하고, 모든 지식을 마크다운(Markdown) 코드로 관리하는 'Knowledge-as-Code' 방법론을 도입합니다.

* **[집필] Obsidian (로컬)**: 사용자가 에이전트의 룰, 페르소나, 지식 데이터를 마크다운 포맷으로 구조화(태깅, 링크)하여 작성합니다.
* **[배포 및 버전 관리] GitHub (클라우드)**: 'Obsidian Git' 무료 플러그인을 통해 로컬에서 작성된 지식이 자동으로 Commit & Push 되어 영구적으로 백업되고 버전이 관리됩니다.
* **[학습 및 인덱싱] VPS (호스팅어)**: 서버의 감시 스크립트(웹훅/크론잡)가 GitHub의 변경 사항을 즉시 Pull 한 뒤, BRENXIA 에이전트(rag_ingest.py)가 이를 쪼개어 ChromaDB에 자동 인덱싱합니다.

## 2. 해결되는 문제점 (Solved Problems)
* **지식의 블랙박스화 방지**: 에이전트가 어떤 지식을 기반으로 대답하는지 옵시디언 그래프를 통해 시각적으로 확인 가능.
* **데이터 유실 및 버전 관리 (Rollback)**: 잘못된 지식을 주입하여 에이전트가 오작동할 경우, GitHub를 통해 즉시 이전 버전 지식으로 복구 가능.
* **서버 관리 리소스 제로화**: 사용자는 복잡한 서버 접속이나 UI 파일 업로드 없이, 로컬 옵시디언 메모장만 관리하면 됨.

## 3. 계정 운영 정책 (Account Policy)
* **구축/테스트 단계**: 
  - Obsidian: 오프라인 사용 (계정 불필요)
  - GitHub: 개인 계정 (`JuneHyeongCho`) 사용
* **정식 런칭 단계**: 
  - GitHub에 무료 `Organization` 계정 생성 후 저장소 이관. (직원 및 권한 관리 용이)

## 4. 향후 구현 단계 (Next Implementation Steps)
1. **로컬 옵시디언 셋업**: 로컬 PC에 Obsidian 설치 및 `BRENXIA-Knowledge` Vault 생성.
2. **Obsidian Git 연동**: 옵시디언과 GitHub 저장소를 연결하여 자동 Push/Pull 테스트.
3. **VPS 자동 Pull 스크립트 작성**: 호스팅어 서버에서 GitHub 변경을 감지하고 주기적으로 최신 마크다운 파일을 다운로드하는 파이프라인 스크립트 구축.
4. **자동 인덱싱 트리거 연동**: 새 파일이 다운로드되면 즉시 `rag_ingest.py`가 백그라운드에서 실행되도록 연결.

---
**[비고]**
본 아젠다는 `agent.brenxia.com` DNS 연결 및 페이퍼클립 기초 테스트가 완전히 종료된 이후, 최우선 고도화 과제로 진행될 예정입니다.
