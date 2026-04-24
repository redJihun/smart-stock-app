# TASK-{NNN}: {제목}

> 작성: Claude Code CLI (관리자) | 대상: Cursor 에이전트 (실행자)
> 생성일: {YYYY-MM-DD}

---

## 배경 (왜 필요한가)

{한두 줄로 작업이 필요한 이유}

## 목표

- [ ] 구체적 목표 1
- [ ] 구체적 목표 2

## 담당 파일 (실행자가 수정할 파일만 명시)

- `issuance_be_fastapi/...` — 역할 설명
- `tests/...` — 역할 설명

---

## Phase 2: 구현 지시

### Agent-A: {담당 범위}

- 담당 파일: `...`
- 구현 내용:
  - ...
  - ...

### Agent-B: {담당 범위} (병렬 가능 시)

- 담당 파일: `...`
- 구현 내용:
  - ...

---

## Phase 3: 검증 명령

```bash
uv run ruff check {모듈 경로}/
uv run ruff format {모듈 경로}/
uv run mypy {모듈 경로}/ --strict
uv run pytest {신규 테스트 파일} -v
uv run pytest tests/ -v   # 전체 회귀
```

---

## 참고 파일 (먼저 읽을 것)

- `...`
- `...`

## 완료 조건

- [ ] ruff 에러 없음
- [ ] mypy --strict 통과
- [ ] pytest 전부 통과
- [ ] RESULT.md 작성 완료 (상태 "✅ 완료")
