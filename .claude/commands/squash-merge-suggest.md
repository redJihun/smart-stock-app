---
name: squash-merge-suggest
description: Analyzes a branch's commit history and diff to suggest a Squash Merge commit message (Pattern C) (does not execute merge)
allowed-tools: ["Bash"]
model: sonnet
---

# /squash-merge-suggest — Squash Merge Commit Message Suggestion

## Role Definition

This command analyzes the entire commit history and changes of the current working branch, and suggests a Squash Merge commit message in the **Pattern C format defined in ADR-0001**.

Strictly prohibited:
- `git merge` execution
- `git commit` execution
- `git push` execution

Allowed:
- `git log` (read-only)
- `git diff` (read-only)
- `git branch` (read-only)

---

## Input Format

```
$ARGUMENTS parsing:
- Target branch (optional, default: master)
  e.g.: /squash-merge-suggest          → target: master
  e.g.: /squash-merge-suggest develop  → target: develop
```

If $ARGUMENTS is empty, `master` is used; if a value is provided, that branch name is used as the target branch.

---

## Execution Steps

### Step 1. Check Current Branch

```bash
git branch --show-current
```

### Step 2. Collect Commit List Relative to Target Branch Common Ancestor

```bash
git log {target}..HEAD --oneline
git log {target}..HEAD --format="%s%n%b%n---"
```

- If the commit count is 0, output "There are no new commits on the current branch compared to {target}." and terminate
- Collect all commit message subjects and bodies

### Step 3. Collect Changed File Stats and Actual Diff

```bash
git diff {target}...HEAD --stat
git diff {target}...HEAD
```

- If the diff is too long (exceeds 500 lines), analyze using only `--stat` results and commit messages
- Infer scope from changed file paths

### Step 4. Infer type/scope from Branch Name

- Branch name pattern: `feat/alerts-recent` → type: `Feat`, scope: `alerts` or primary changed domain
- **Prioritize actual changes over branch name** (e.g., if the actual main purpose is refactoring, use `Refac`)

### Step 5. Generate Pattern C Message

Synthesize collected information (commit message list + diff stat + branch name):

- **type**: Classify change purpose (Feat/Fix/Docs/Refac/Chore/Test/Style)
  - Reference: type list in [commit-message-suggest.md](commit-message-suggest.md)
- **scope**: Primary changed domain (inferred from changed file paths; if multiple domains, use only the key one)
- **one-line summary**: A Korean summary within 50 characters representing the entire branch work
- **reason for change (Why)**: Extract common purpose/background from commit messages (why this work was needed)
- **Changes list**: Summarize by each commit or file change unit (3-5 items)

---

## Output Format

Output in the following format:

```
---
**Squash Merge Commit Message Suggestion**

Current branch: {branch}
Target branch: {target}
Included commits: {N}

**[Suggested Message]**
```
<type>(<scope>): <one-line summary>

<reason for change — why this work was needed>

Changes:
- detailed change item 1
- detailed change item 2
- detailed change item 3

See also: docs/architecture-decision-records/0001-squash-merge-strategy.md
```

**Selection Rationale**
- **type selection**: {reason}
- **scope selection**: {reason}
- **Why summary basis**: {which commit messages/diff was it extracted from}
---

> The merge is not executed directly. Copy the message and use it.
```

---

## Completion Report

Include the following information after message suggestion is complete:

```
✓ Squash Merge message suggestion complete
  Current branch: {branch}
  Target branch: {target}
  Included commits: {N}

Copy the [Suggested Message] above and use it when running git merge.
```
