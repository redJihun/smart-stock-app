# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Communication Language

이 프로젝트의 주 사용자는 한국어 사용자입니다. Claude는 이 저장소에서 작업할 때 **한국어를 주 언어**로 사용해야 합니다.
- 사용자와의 모든 대화, 설명, 질문은 한국어로 작성합니다.
- 코드 주석, 커밋 메시지 등 기술적 결과물은 프로젝트 컨벤션에 따릅니다.

## Project Overview

A Python sandbox for stock market pricing and trading strategies (주식 시세, 거래 전략 등 샌드박스).

## Development Setup

확정 스택: **uv** (패키지 매니저) / **ruff** (린트·포맷) / **mypy** (타입 체크) / **pytest** (테스트) / **Jupyter** (노트북)

환경 구성 및 주요 명령어:

```bash
# 의존성 설치
uv sync

# 개발 의존성 포함 설치
uv sync --group dev

# 테스트
pytest

# 린트·포맷 확인
ruff check .
ruff format .

# 타입 체크
mypy .
```

## Project Structure

```
smart-stock-app/
├── src/
│   └── smart_stock/
│       ├── data/           # 데이터 수집·로더 (fdr, yfinance 래퍼)
│       ├── strategies/     # 거래 전략 (추상 클래스 상속)
│       ├── analysis/       # 분석 모듈
│       └── utils/          # 공통 유틸
├── notebooks/              # Jupyter 노트북 (탐색·실험)
├── tests/                  # pytest 테스트
├── docs/                   # 문서 (work-logs, ADR)
│   ├── README.md
│   ├── work-logs/
│   └── architecture-decision-records/
├── data/                   # .gitignore 처리
│   ├── raw/                # 원본 데이터
│   └── processed/          # 가공 데이터
└── pyproject.toml
```

## Naming Conventions

- **디렉토리·소스 파일**: `snake_case`
- **클래스**: `PascalCase`
- **함수·변수**: `snake_case`, 함수는 동사 시작
- **상수**: `UPPER_SNAKE_CASE`
- **노트북 파일**: `kebab-case.ipynb`
- **문서 파일**: `kebab-case.md`

## Git Convention

커밋 메시지는 **한국어**로 작성한다. 형식:

```
<type>(<scope>): <한 줄 요약>

<변경 이유 — 왜 이 작업이 필요했는지>

Changes:
- 세부 변경 항목 1
- 세부 변경 항목 2
```

타입: `Feat` / `Fix` / `Docs` / `Style` / `Refac` / `Test` / `Chore`

브랜치 네이밍: `feat/기능명`, `fix/버그명`, `docs/문서명`, `chore/작업명`, `refac/대상명`

병합 전략: **Squash Merge** 기본 (단일 핫픽스는 Fast-forward)

커밋 메시지 제안 시 항상 패턴C 형식을 사용한다. `git commit`은 사용자 확인 후 실행한다.

## Testing

- `pytest` 사용
- 테스트 파일: `test_{모듈명}.py`
- 테스트 함수: `test_{기능}_{시나리오}()`
- 전략·분석 모듈은 테스트 필수, 노트북 탐색 코드는 제외

## Notebooks

- `notebooks/` 아래 파일명은 `kebab-case.ipynb`
- 탐색이 완료된 로직은 `src/smart_stock/` 모듈로 이동한다
- 노트북 내 데이터 파일 경로는 `data/raw/` 또는 `data/processed/` 기준으로 작성한다
- `data/` 디렉토리는 `.gitignore` 대상 — 데이터 파일을 커밋하지 않는다

## Data Sources

| 라이브러리 | 용도 |
|---|---|
| `FinanceDataReader` (fdr) | 국내 주식 메인 (KOSPI, KOSDAQ, KRX) |
| `yfinance` | 해외 주식 보조 (미국, 글로벌) |

## Docs Management

```
docs/
  README.md                              # 전체 문서 인덱스 (필수)
  work-logs/                             # 주차별 업무일지 + 장기 관리 문서
    README.md
    BACKLOG.md                           # 장기 예정 업무, 기술부채
    NOTES.md                             # 아이디어, 메모, 참고 링크
    {YYMMDD시작}-{YYMMDD종료}-W{주차}.md  # 주차별 업무일지
  architecture-decision-records/         # ADR
    README.md                            # ADR 인덱스 + 상태 목록
    template.md
    {NNNN}-{주제-kebab-case}.md          # 개별 ADR
```

문서 추가 시 갱신 대상:

| 추가한 문서 | 함께 갱신할 인덱스 |
|---|---|
| ADR (`architecture-decision-records/*.md`) | `architecture-decision-records/README.md` + `docs/README.md` |
| 주차 업무일지 (`work-logs/*.md`) | `work-logs/README.md` |
| 일반 개발 문서 (`docs/*.md`) | `docs/README.md` |

## ADR 작성 기준

다음 조건 중 하나 이상 해당하면 ADR 작성을 제안한다:

- 되돌리기 어려운 기술 결정 (라이브러리 선택, 아키텍처 패턴 등)
- 여러 선택지를 비교해 채택한 결정
- 나중에 맥락 없이 보면 이상하게 보일 수 있는 결정

ADR 추가 후 두 인덱스(`architecture-decision-records/README.md`, `docs/README.md`)를 반드시 갱신한다.
