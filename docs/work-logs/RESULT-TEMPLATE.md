# RESULT.md — 작업 결과 보고

> 실행자(Haiku) 세션이 작성 → 관리자(Sonnet) 세션이 검수
> 각 Agent는 자신의 섹션에만 기록

---

## 현재 작업: TASK-{NNN} — {제목}

**상태**: 🔄 진행 중

---

## Phase 2: 구현

### Agent-구현{이름}
**파일**: `{파일 경로}`
**상태**: ⬜ 대기 중

**구현 내용**:
- (완료 후 작성)

---

## Phase 3: 검증

### ruff check
```bash
uv run ruff check {모듈 경로}/
```
**결과**: ⬜ 미실행

### ruff format
```bash
uv run ruff format {모듈 경로}/
```
**결과**: ⬜ 미실행

### mypy strict
```bash
uv run mypy {모듈 경로}/ --strict
```
**결과**: ⬜ 미실행

### pytest (신규 테스트)
```bash
uv run pytest {신규 테스트 파일들} -v
```
**결과**: ⬜ 미실행

### pytest (전체 테스트 스위트)
```bash
uv run pytest tests/ -v
```
**결과**: ⬜ 미실행

---

## 최종 상태

**상태**: ⬜ 진행 중

**완료 기준 체크리스트**:
- [ ] (완료 후 기록)
