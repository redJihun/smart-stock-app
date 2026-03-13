# ADR-0003: 패키지 매니저 uv 선택

| 항목 | 내용 |
|------|------|
| 상태 | Accepted |
| 날짜 | 2026-03-13 |
| 결정자 | 홍지훈 |

---

## 맥락 (Context)

Python 프로젝트의 패키지 매니저와 가상환경 관리 도구를 선택해야 한다.
후보는 `pip`, `poetry`, `pdm`, `pipenv`, `uv`이다.

| 도구 | 속도 | pyproject.toml | 가상환경 통합 | Python 버전 관리 |
|------|------|---------------|------------|----------------|
| pip | 보통 | 부분 | ✗ | ✗ |
| poetry | 보통 | ✓ | ✓ | ✗ |
| pdm | 보통 | ✓ | ✓ | ✗ |
| pipenv | 느림 | ✗ | ✓ | ✗ |
| uv | 매우 빠름 | ✓ | ✓ | ✓ |

## 결정 (Decision)

**uv**를 패키지 매니저로 채택한다.

- Astral 제공, Rust 기반으로 pip 대비 10~100배 빠른 설치 속도
- `pyproject.toml` 표준 지원 (PEP 517/518 준수)
- 가상환경 생성·관리, Python 버전 관리까지 통합
- 병렬 프로젝트 issuance-fastapi에서 이미 사용 중 — 워크플로우 일관성

### 참고자료 (References)

- [uv 공식 문서](https://docs.astral.sh/uv/)

## 결과 (Consequences)

### 이점 (Benefits)

- 의존성 설치 속도가 매우 빠름 — 반복 실험 환경 재구성 부담 감소
- `pyproject.toml` 단일 파일로 프로젝트 설정 통합
- `uv sync` 한 명령어로 환경 재현 가능

### 단점 (Drawbacks)

- pip에 비해 아직 생태계가 작음 (일부 CI 환경에서 별도 설치 필요)
- `requirements.txt` 대신 `pyproject.toml`이 표준이 되어 기존 pip 워크플로우와 다름

### 리스크 (Risks)

- Astral 스타트업 의존 — 향후 정책 변화 가능성 있으나 오픈소스이므로 포크 가능
