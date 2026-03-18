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

### 파일 길이 원칙

- 각 모듈 파일은 **500줄 이내**로 유지
- 이를 초과할 경우 자동으로 모듈 분리/리팩토링 제안
- 너무 큰 파일은 Claude가 효율적으로 읽고 이해하기 어려움

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

### 커밋 타이밍

기능이나 버그 수정이 완료되면 자동으로 커밋 메시지를 제안한다. 사용자 확인 후 실행.

## Testing

- `pytest` 사용
- 테스트 파일: `test_{모듈명}.py`
- 테스트 함수: `test_{기능}_{시나리오}()`
- 전략·분석 모듈은 테스트 필수, 노트북 탐색 코드는 제외

### TDD 디버깅 접근법

버그를 수정할 때는 다음 3단계를 따른다:

1. **재현 테스트 작성** (실패하는 테스트)
   - 버그 현상을 재현하는 테스트 코드를 먼저 작성하고 실행
   - 이 테스트는 반드시 실패해야 함

2. **원인 분석**
   - 가능한 원인들을 제시하고 확인 방법 제안
   - 불필요한 수정은 하지 않음 (사용자와 함께 원인 파악)

3. **코드 수정**
   - 원인을 파악한 후 테스트가 통과될 때까지 수정
   - 수정 전 항상 변경 범위를 사용자에게 알림

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

자세한 문서 구조, 갱신 규칙, ADR 기준 → `.claude/rules/docs-management.md` 참조

## Workflow

### 복잡한 작업은 플랜 모드 우선

- **단순 변경**: 바로 수정 (한 파일, 버그픽스, 작은 기능)
- **복잡한 구현**: `EnterPlanMode`로 설계 → 사용자 확인 → 실행
  - 여러 파일을 수정하는 작업
  - 아키텍처 변경이 필요한 작업
  - 다양한 접근 방법이 가능한 작업

### 세션 관리

- 작업이 완료되면 커밋 제안 → 사용자 실행
- 컨텍스트가 충분하면 계속 작업 (세션 유지)
- 필요시 `/compact` (컨텍스트 압축) 또는 `/clear` (새 세션 시작) 사용자 명령 대기
- 에이전트 사이클에서의 세션 관리 타이밍 → `.claude/rules/task-cycle.md` 참조
- **유의미한 대화 종료 후** CLAUDE.md 또는 MEMORY.md 갱신 제안

## 에이전트 팀 워크플로우

자세한 세션 구성, 통신 채널, 패턴, Haiku 활용 기준, Worktree 활용 → `.claude/rules/agent-workflow.md` 참조

**3단계 사이클 규칙** (계획/실행/검토 체크리스트, 커밋 생성 규칙, MEMORY.md 갱신 항목) → `.claude/rules/task-cycle.md` 참조

**TASK.md 템플릿** → `docs/work-logs/TASK-TEMPLATE.md`
**RESULT.md 템플릿** → `docs/work-logs/RESULT-TEMPLATE.md`

핵심 요약:
- 터미널1(Sonnet 관리자) → TASK.md 작성 → 터미널2(Haiku 실행자) → RESULT.md 보고
- 구현 Agent는 `isolation: "worktree"` 로 격리 실행
- 서브에이전트 최대 4~5개, Agent당 단일 책임

## 변경 범위 확인 원칙

수정 전에는 항상:

1. 대상 파일을 읽고 현재 상태 파악
2. **변경이 영향을 주는 파일/모듈 범위**를 사용자에게 명확히 알림
3. 사용자 확인 후 수정 실행

과도한 변경을 방지하고, 예상치 못한 부작용을 줄이기 위함.

## 코드 리뷰 체크리스트

구현 완료 후 자동으로 확인하고 결과 보고:

- [ ] **린트**: `ruff check .` 통과
- [ ] **포맷**: `ruff format .` 적용됨
- [ ] **타입**: `mypy .` 통과
- [ ] **테스트**: `pytest` 통과 (해당 모듈)

모든 항목이 통과할 때까지 수정 제안.

## Compact Instructions

`/compact` 실행 시 다음 정보를 우선 보존한다:

- 현재 진행 중인 TASK 번호와 상태
- 구현 완료된 파일 목록과 테스트 통과 여부
- 미결 이슈 및 다음 단계
- 아키텍처 결정 사항 (되돌리기 어려운 것)
