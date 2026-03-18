# TASK.md — 실행자 작업 지시서

> 관리자(Sonnet) 세션이 작성 → 실행자(Haiku) 세션이 읽고 실행
> 완료 후 결과는 `RESULT.md`에 기록

---

## 현재 작업

### 작업 ID: TASK-{NNN}
### 제목: {제목}

### 배경

{왜 이 작업이 필요한가 — 이전 TASK와의 연결고리}

---

## 참고 파일 (먼저 읽을 것)

- `{파일 경로}` — {읽는 이유}

---

## 구현 명세

> 공통 제약은 `.claude/rules/task-cycle.md` 참조 (from __future__, 500줄, mypy strict 등)

---

### Phase 2: 구현 ({N}개 파일 — 병렬 가능)

---

#### Agent-구현{이름} → `{파일 경로}` (신규/수정)

{구현 명세 또는 코드 스켈레톤}

파일 단위 검증:
```bash
uv run ruff check {파일 경로} && uv run mypy {파일 경로} --strict
```

---

### Phase 3: 검증

#### Agent-검증

```bash
uv run ruff check {모듈 경로}/
uv run ruff format {모듈 경로}/
uv run mypy {모듈 경로}/ --strict
uv run pytest {신규 테스트 파일들} -v
uv run pytest tests/ -v
```

오류 발생 시 해당 파일 수정 후 재실행.
결과를 `RESULT.md`의 각 섹션에 기록.

---

## 완료 기준

- [ ] {파일 경로} 생성/수정
- [ ] ruff check 통과
- [ ] ruff format 적용
- [ ] mypy --strict 통과
- [ ] pytest 신규 테스트 전체 통과
- [ ] pytest 전체 테스트 스위트 통과 (기존 {N}개 + 신규)
- [ ] `RESULT.md` 갱신 완료
