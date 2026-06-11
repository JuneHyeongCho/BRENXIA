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
