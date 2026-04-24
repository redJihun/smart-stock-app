# CLAUDE.md Token Optimization Design

**Date:** 2026-04-24
**Goal:** Reduce CLAUDE.md from 204 lines to ~150 lines and convert all project docs to English for token efficiency.
**User-facing output (responses, commit messages) remains Korean.**

---

## Phase 0: Documentation Discovery

### Sources Consulted
- `CLAUDE.md` — 204 lines, full content confirmed
- `.claude/rules/workflow.md` — 82 lines, 5 sections
- `.claude/rules/critical-rules.md` — already contains Section 3: Git Workflow (full convention)
- `.claude/CLAUDE.md` — template system; states "200 lines max for CLAUDE.md"

### Allowed Edits
- Move content into existing rules files only (no new files)
- English for all doc files; Korean only for responses and commit messages

### Anti-patterns to Avoid
- Creating new `.claude/rules/*.md` files
- Removing content that Claude references every turn (naming conventions, project structure, scope constraints)
- Translating commit message format examples to English (they must stay Korean)

---

## Phase 1: Append 3 sections to `workflow.md`

**File:** `.claude/rules/workflow.md`
**Current:** 82 lines
**Change:** Append 3 sections at end of file (before final extended guidance line)

### Content to Add

```markdown
---

## TDD Debugging Approach

When fixing bugs, follow these 3 steps:

1. **Write a failing test** — reproduce the bug; this test must fail first
2. **Analyze root cause** — list possible causes and propose verification steps; do not modify code yet
3. **Fix the code** — modify until test passes; notify user of change scope before editing

---

## Code Review Checklist

Run automatically after every implementation and report results:

- [ ] `ruff check .` passes
- [ ] `ruff format .` applied
- [ ] `mypy .` passes
- [ ] `pytest` passes (relevant module)

Fix all failures before suggesting commit.

---

## Compact Instructions

On `/compact`, preserve:

- Current TASK number and status
- List of implemented files and test pass/fail results
- Unresolved issues and next steps
- Architecture decisions (hard to reverse)
```

**Verification:**
- `workflow.md` line count increases by ~30 lines (~112 total)
- Grep confirms "TDD Debugging", "Code Review Checklist", "Compact Instructions" headings exist

---

## Phase 2: Rewrite `CLAUDE.md` in English (~150 lines)

**File:** `CLAUDE.md`
**Change:** Full rewrite — English conversion + compression

### Final content

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Communication Language

- All project docs (CLAUDE.md, rules, specs): **English** (token efficiency)
- All responses and explanations to user: **Korean**
- Commit messages: **Korean** (project convention)

## Project Overview

Python sandbox for stock market pricing and trading strategies.

## Development Setup

Stack: **uv** / **ruff** / **mypy** / **pytest** / **Jupyter**

| Command | Purpose |
|---|---|
| `uv sync --group dev` | Install dependencies |
| `pytest` | Run tests |
| `ruff check . && ruff format .` | Lint & format |
| `mypy .` | Type check |

## Project Structure

```
smart-stock-app/
├── src/
│   └── smart_stock/
│       ├── data/           # Data collection & loaders (fdr, yfinance wrappers)
│       ├── strategies/     # Trading strategies (abstract class inheritance)
│       ├── analysis/       # Analysis modules
│       └── utils/          # Common utilities
├── notebooks/              # Jupyter notebooks (exploration & experiments)
├── tests/                  # pytest tests
├── docs/                   # Docs (work-logs, ADR)
│   ├── README.md
│   ├── work-logs/
│   └── architecture-decision-records/
├── data/                   # .gitignore — do not commit data files
│   ├── raw/
│   └── processed/
└── pyproject.toml
```

**File length:** Keep each module file under **500 lines**. Suggest splitting if exceeded.

## Naming Conventions

- **Directories & source files**: `snake_case`
- **Classes**: `PascalCase`
- **Functions & variables**: `snake_case`, functions start with a verb
- **Constants**: `UPPER_SNAKE_CASE`
- **Notebook files**: `kebab-case.ipynb`
- **Doc files**: `kebab-case.md`

## Git Convention

Commit messages in **Korean**, Pattern C format:

```
<type>(<scope>): <한 줄 요약>

<변경 이유>

Changes:
- 항목 1
- 항목 2
```

Types: `Feat` / `Fix` / `Docs` / `Style` / `Refac` / `Test` / `Chore`
Branch naming: `feat/`, `fix/`, `docs/`, `chore/`, `refac/`
Merge strategy: **Squash Merge** by default
Always suggest commit message after completion; run `git commit` only after user confirmation.
Full git convention details → `.claude/rules/critical-rules.md` Section 3

## Testing

- Use `pytest` / File: `test_{module}.py` / Function: `test_{feature}_{scenario}()`
- Tests required for strategy & analysis modules; notebooks excluded
- TDD debugging (3-step) → `.claude/rules/workflow.md`

## Notebooks

- File names: `kebab-case.ipynb` under `notebooks/`
- Move finalized logic to `src/smart_stock/` modules
- Data file paths: use `data/raw/` or `data/processed/` as base
- `data/` is `.gitignore`-tracked — do not commit data files

## Data Sources

| Library | Purpose |
|---|---|
| `FinanceDataReader` (fdr) | Korean stocks (KOSPI, KOSDAQ, KRX) |
| `yfinance` | Foreign stocks (US, global) |

## Docs Management

Doc structure, update rules, ADR criteria → `.claude/rules/docs-management.md`

## Workflow

- **Simple changes**: Edit directly (single file, bug fix, small feature)
- **Complex work**: `EnterPlanMode` → user confirmation → execute
  - Multiple files, architecture changes, or multiple valid approaches
- Always read target file before editing; notify user of affected scope
- After implementation: run checks, then suggest commit (execute only after user confirmation)

Details, TDD debugging, code review checklist, compact instructions → `.claude/rules/workflow.md`

## Agent Team Workflow

Terminal1 (Sonnet manager) → writes TASK.md → Terminal2 (Haiku executor) → reports RESULT.md
Executor forbidden: `git commit`, `git push`, arbitrary work without manager judgment
Max 4-5 parallel subagents; single responsibility per agent; use `isolation: "worktree"`

Full details → `.claude/rules/workflow.md`

## Scope Constraints

- Modify only requested files; minimum changes for bug fixes
- Do not create files, add docstrings/comments/type hints, or design for future requirements unless asked
- Do not use destructive shortcuts to unblock yourself — investigate first
- Protected files (confirm before modifying): `config.yml`, `.env`, `docker-compose*.yml`, `CLAUDE.md`
- Delete or move files only after user confirmation
```

**Verification:**
- Line count: target < 200
- No Korean in prose sections (except commit message format example)
- All removed sections exist in `workflow.md` (TDD / checklist / compact)
- Communication Language section explicitly states English-docs / Korean-responses rule

---

## Phase 3: Verify

1. Count lines in `CLAUDE.md`: must be < 200
2. Grep `workflow.md` for: "TDD Debugging", "Code Review Checklist", "Compact Instructions"
3. Grep `CLAUDE.md` for Korean prose outside commit format block — should be none
4. Confirm `critical-rules.md` unchanged

---

## Summary

| File | Before | After | Delta |
|---|---|---|---|
| `CLAUDE.md` | 204 lines, Korean | ~150 lines, English | -25% tokens |
| `.claude/rules/workflow.md` | 82 lines | ~112 lines | +30 lines |
| `.claude/rules/critical-rules.md` | unchanged | unchanged | — |
