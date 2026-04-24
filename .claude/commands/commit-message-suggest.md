---
description: Analyzes staged changes and suggests commit messages (does not execute commit)
allowed-tools: Bash
model: haiku
---

Analyze the staged git changes and suggest commit message candidates.
Suggested commit message must be in "Korean", this commit message's for Korean user.

## Execution Steps

1. `git diff --cached --stat` — Check the list of changed files
2. `git diff --cached` — Check the actual change contents
3. `git log --oneline -5` — Check the actual commit style of this project

## Commit Message Rules (Project Convention)

### Header Format (required, max 50 chars)

```
<type>(<scope>): <description in English>
```

### Type List

| type | When to Use |
|------|-------------|
| `Feat` | Adding a new feature |
| `Fix` | Bug fix |
| `Docs` | Documentation changes only (.md, .mdc files) |
| `Style` | Code formatting, missing semicolons, etc. — changes with no effect on behavior |
| `Refac` | Code refactoring (no behavior change) |
| `Test` | Adding or modifying test code |
| `Chore` | Build, package, or config file changes (requirements.txt, docker-compose, etc.) |

### Scope Selection Criteria

Use the domain/module name of the changed files:
- `domain/board/crud/dashboard.py` → scope: `dashboard`
- `domain/board/crud/session.py` → scope: `sessions`
- `routers/workinfos.py` → scope: `workinfo`
- `.claude/commands/*.md`, `.cursor/rules/*.mdc` → scope: `chore` or the file's subject
- Multiple domains changed simultaneously → use the most central domain or a higher-level concept

### Body (optional, wrap at 72 chars)

When the change is complex or a reason needs to be explained:
```
<type>(<scope>): <one-line summary>

<reason for change — why this work was necessary>

Changes:
- Detail item 1
- Detail item 2
```

### Writing Guidelines

- No period at the end of the header
- Write the body focused on "why" rather than "what"
- Body may be omitted for a single `Fix` commit
- Use the `Docs` type only when changing `.mdc` (Cursor rules) or `.md` (documentation) files
- Use the `Chore` type for build/environment configuration such as `requirements.txt`, `docker-compose.yml`, `.env.example`
- Must use Korean language for suggested commit message(header, body, changes, ...)

## Output Format

If no staged changes: output only "No staged changes."

If staged changes exist, output in the following format:

---
**Commit Message Suggestion**

**[Option 1]** (header only, simple case)
```
<type>(<scope>): <description>
```

**[Option 2]** (with body, complex changes)
```
<type>(<scope>): <description>

<reason for change>

Changes:
- item1
- item2
```

**Selection Rationale**: one line each for type selection reason + scope selection reason
---

> The commit is not executed automatically. Copy the message you prefer and use it yourself.
