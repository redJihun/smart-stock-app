# 작업 사이클 규칙 (계획 → 실행 → 검토)

> 매 TASK마다 반복하는 3단계 표준 절차. 각 단계에서 이 파일을 참조한다.

---

## 전체 흐름

```
1단계 관리자(Sonnet, 고지능): TASK.md 작성 + RESULT.md 초기화
2단계 실행자(Haiku or Cousor, 저지능):  TASK.md 읽고 구현 → RESULT.md 기록
3단계 관리자(Sonnet, 고지능): RESULT.md 검토 → 코드 검토 → MEMORY.md 갱신 → 커밋 제안
```

---

## 1단계: 계획 (관리자)

1. `EnterPlanMode`로 설계 확정
2. `docs/work-logs/TASK-TEMPLATE.md` 복사 → `TASK.md`에 붙여넣기 후 빈 칸 채우기
3. `docs/work-logs/RESULT-TEMPLATE.md` 복사 → `RESULT.md`에 붙여넣기 (상태 초기화)
4. 실행자에게 "TASK.md 확인해줘" 전달

---

## 2단계: 실행 (실행자)

1. `TASK.md` 읽기 → 참고 파일 먼저 읽기
2. Phase 2 (구현) → 각 Agent 담당 파일만 수정
3. Phase 3 (검증) → 검증 명령 순서대로 실행, 실패 시 수정 후 재실행
4. 각 Phase 완료 후 `RESULT.md` 해당 섹션 기록
5. 모든 Phase 완료 → `RESULT.md` 최종 상태 "✅ 완료"로 갱신

> **⛔ 실행자 금지 행동**
> - `git commit` / `git push` 절대 금지 — 커밋은 관리자(Sonnet) 전용
> - 작업 완료 후 관리자의 다음 지시를 기다린다 (자율 판단으로 추가 작업 진행 금지)

---

## 3단계: 검토 (관리자)

### 검토 순서

- [ ] `RESULT.md` 읽기 — 검증 결과(ruff/mypy/pytest) 확인
- [ ] 신규/수정 소스 파일 읽기 — 핵심 로직, 타입 힌트, 예외 처리 확인
- [ ] 신규 테스트 파일 읽기 — 커버리지 충분한지, 격리 잘 됐는지 확인
- [ ] MEMORY.md 갱신 (아래 규칙 참조)
- [ ] 커밋 메시지 작성 (아래 규칙 참조)

### MEMORY.md 갱신 필수 항목

매 TASK 완료 시 반드시 갱신:

1. **"구현된 모듈 현황" 섹션** — 신규 파일 + 테스트 개수 추가
2. **"Phase 0 백로그 순서" 테이블** — 해당 TASK 상태 `대기` → `✅ 완료`
3. **전체 테스트 수** — `(기존 N개 + 신규 M개 = 합계)`
4. **"구현 패턴 메모"** — 이번 TASK에서 새로 발견된 패턴/트릭 추가 (없으면 생략)

### 커밋 메시지 생성 규칙

RESULT.md의 내용에서 자동 추출:

```
{타입}({scope}): {TASK 제목} ({TASK-NNN})

{TASK 배경 한 줄 요약 — "왜" 필요했는지}

Changes:
- {RESULT.md Phase2 Agent별 "구현 내용" 항목들}
- 전체 테스트: {기존} → {신규}개 (+{증가량})
```

**타입 선택 기준:**
- 신규 모듈/기능 추가 → `Feat`
- 기존 코드 수정/개선 → `Fix` 또는 `Refac`
- 테스트만 추가 → `Test`
- 문서/설정 변경 → `Docs` / `Chore`

---

## 세션 관리 타이밍

| 시점 | 세션 | 액션 | 이유 |
|------|------|------|------|
| 2단계(실행) 완료 후 | 실행자(Haiku) | `/clear` | 구현 컨텍스트 불필요, 다음 TASK를 위해 초기화 |
| 3단계(검토) 완료 후 | 관리자(Sonnet) | `/compact` | 설계·검토 컨텍스트 경량화, 다음 TASK 설계를 위해 유지 |

---

## 공통 코드 제약 (TASK.md에 매번 복사 불필요, 여기서 참조)

실행자가 구현할 때 항상 적용:

- `from __future__ import annotations` 첫 줄
- pandas 만으로 구현 (numpy 직접 사용 금지, math 모듈 허용)
- 각 파일 **500줄 이내**
- 한국어 docstring (NumPy 스타일: Parameters / Returns / Raises / Notes)
- mypy strict 통과
- Python 3.11+ 호환 (`StrEnum`, `from collections.abc import Callable` 등)

---

## 표준 검증 명령

```bash
uv run ruff check {모듈 경로}/
uv run ruff format {모듈 경로}/
uv run mypy {모듈 경로}/ --strict
uv run pytest {신규 테스트 파일들} -v
uv run pytest tests/ -v   # 전체 회귀 테스트
```
