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

## Compact Instructions

Code review checklist and `/compact` preservation items → `.claude/rules/workflow.md`
