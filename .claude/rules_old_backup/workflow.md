# Agent Team Workflow (B+A Hybrid)

## Team Composition

| Role | Model | Responsibility |
|------|-------|---------------|
| Manager | Sonnet / Opus | Design (EnterPlanMode), write TASK.md, code review, git commit/push |
| Executor | Haiku / Cursor | Receive TASK.md → implement → record in RESULT.md → wait (git forbidden) |

> **Executor forbidden actions**: `git commit`, `git push`, proceeding with arbitrary work without additional judgment

## File-Based Communication

```
docs/work-logs/
  TASK.md    ← Manager: task instructions
  RESULT.md  ← Executor: task result report
```

---

## Standard Workflow (3 Phases)

### Phase 1: Planning (Manager)

1. Finalize design with `EnterPlanMode`
2. Write TASK.md (specify assigned files), initialize RESULT.md
3. Send "Check TASK.md" to executor

### Phase 2: Implementation (Executor)

1. Read TASK.md, read reference files first
2. Modify only assigned files using parallel Agents (single responsibility per agent, max 4-5)
3. Record in RESULT.md after phase completion

### Phase 3: Verification & Commit (Sequential)

**Verifier:**
1. Run ruff + pytest, record results in RESULT.md
2. Fix and re-run on failure

**Manager review:**
1. Read RESULT.md (check verification results)
2. Read new/modified code (check for bugs/design violations)
3. Update MEMORY.md, propose commit

---

## Haiku Usage Criteria

```
Sonnet/Opus handles directly:
  - Architecture decisions, new core business logic
  - Security code (authentication, query binding, authorization)
  - Code review (finding bugs, design violations)

Delegatable to Haiku:
  - Implementing already-designed code (following existing patterns)
  - CRUD creation, tests, boilerplate
  - Lint/format fixes, documentation updates
```

> **Decision criteria**: Abundant internet examples and easy to revert → Haiku. First-time design or high failure cost → Sonnet.

---

## Subagent Delegation Principles

- **Single responsibility**: Keep scope narrow (separate exploration/implementation/verification)
- **Isolation**: Use `isolation: "worktree"` for implementation to isolate from main
- **Recording**: Each Agent records in its own section of RESULT.md
- **Count limit**: Max 4-5 (beyond that, context cost increases rapidly)

---

## Parallel Work Safety Rules

1. **Do not modify the same file simultaneously**
2. **Assign role names to each session** (plan, implement, review, research)
3. **Have a file to collect results** (TASK.md, RESULT.md, handoff.md)

Parallelizable: exploration, comparative analysis, independent file modifications
Not parallelizable: simultaneous modification of the same file, sequential dependencies

---

## Session Management Timing

| Timing | Action | Reason |
|--------|--------|--------|
| After execution | `/clear` (executor) | Prepare for next TASK |
| After review | `/compact` (manager) | Maintain design context, prepare for next design |

---

## Common Code Constraints

- Files **500 lines or fewer**
- Python 3.11+ compatible
- Follow existing patterns (Key Patterns in CLAUDE.md)

---

## Standard Verification Commands

```bash
uv run ruff check {path}/
uv run ruff format {path}/
uv run pytest {test file} -v
uv run pytest tests/ -v  # Full regression test
```
