# 문서 인덱스

프로젝트 문서를 목적별로 빠르게 찾을 수 있도록 정리한 인덱스입니다.

---

## 1) 업무 관리

- [`work-logs/README.md`](./work-logs/README.md) — 업무일지 인덱스
- [`work-logs/BACKLOG.md`](./work-logs/BACKLOG.md) — 장기 예정 업무 및 기술부채 목록
- [`work-logs/NOTES.md`](./work-logs/NOTES.md) — 아이디어, 메모, 참고 링크

---

## 2) 아키텍처 결정 기록 (ADR)

기술적 결정 사항과 그 근거를 기록합니다.

- [`architecture-decision-records/README.md`](./architecture-decision-records/README.md) — ADR 인덱스

| 번호 | 제목 | 상태 |
|------|------|------|
| [ADR-0001](./architecture-decision-records/0001-squash-merge-strategy.md) | Squash Merge + 패턴C 커밋 메시지 전략 채택 | Accepted |
| [ADR-0002](./architecture-decision-records/0002-data-source-selection.md) | 데이터 소스 선택 (FinanceDataReader + yfinance) | Accepted |
| [ADR-0003](./architecture-decision-records/0003-package-manager-uv.md) | 패키지 매니저 uv 선택 | Accepted |
| [ADR-0004](./architecture-decision-records/0004-notebook-jupyter.md) | 노트북 도구 Jupyter 선택 | Accepted |
| [ADR-0005](./architecture-decision-records/0005-cache-format-selection.md) | 로컬 캐시 포맷 선택 (Parquet) | Accepted |
| [ADR-0006](./architecture-decision-records/0006-agent-team-workflow.md) | 에이전트 팀 워크플로우 채택 (멀티 터미널 + 서브에이전트) | Accepted |
| [ADR-0007](./architecture-decision-records/0007-kis-api-intraday.md) | 한국 분봉 데이터 소스로 KIS API 선택 | Accepted |

---

## 3) 개발·분석 문서

일반 개발 문서, 전략 설계, 데이터 소스 관련 문서는 `docs/` 루트에 추가합니다.

| 파일 | 설명 |
|------|------|
| [`PRD.md`](./PRD.md) | 제품 요구사항 정의서 (Product Requirements Document) |
