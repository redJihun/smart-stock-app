# Architecture Decision Records (ADR)

아키텍처 및 기술 결정 사항을 기록합니다.
되돌리기 어렵거나, 나중에 "왜 이렇게 했지?" 라는 질문이 나올 만한 결정을 대상으로 합니다.

---

## 작성 기준

다음 조건 중 하나 이상 해당하면 ADR을 작성합니다:

- 되돌리기 어려운 기술 결정 (데이터 소스 선택, 아키텍처 패턴 등)
- 여러 선택지를 비교해 채택한 결정
- 나중에 맥락 없이 보면 이상하게 보일 수 있는 결정

새 ADR 작성 시 [template.md](./template.md)를 복사하여 사용합니다.

---

## ADR 목록

| 번호 | 제목 | 상태 | 날짜 |
|------|------|------|------|
| [ADR-0001](./0001-squash-merge-strategy.md) | Squash Merge + 패턴C 커밋 메시지 전략 채택 | Accepted | 2026-03-13 |
| [ADR-0002](./0002-data-source-selection.md) | 데이터 소스 선택 (FinanceDataReader + yfinance) | Accepted | 2026-03-13 |
| [ADR-0003](./0003-package-manager-uv.md) | 패키지 매니저 uv 선택 | Accepted | 2026-03-13 |
| [ADR-0004](./0004-notebook-jupyter.md) | 노트북 도구 Jupyter 선택 | Accepted | 2026-03-13 |

---

## 상태값 정의

| 상태 | 설명 |
|------|------|
| `Proposed` | 검토 중, 아직 결정되지 않음 |
| `Accepted` | 채택됨, 현재 적용 중 |
| `Deprecated` | 더 이상 유효하지 않음 |
| `Superseded by ADR-XXXX` | 다른 ADR로 대체됨 |
