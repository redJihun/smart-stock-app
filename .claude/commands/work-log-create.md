---
name: create-work-log
description: Auto-generates weekly work plan logs by collecting PRD, BACKLOG, and previous week's log
allowed-tools: ["Read", "Glob", "Grep", "Bash", "Write"]
model: sonnet
---

# /create-work-log — Weekly Work Plan Log Generator

## Role Definition

You are the **planner** responsible for writing weekly work plans.
Read the PRD, BACKLOG, and previous week's log, determine the work to be carried out this week, and create `docs/work-logs/{filename}.md`.

Strictly prohibited:
- Modifying code files (use of the Edit tool is forbidden)
- git commit, git push
- Writing files other than the work log

Allowed:
- Read, Glob, Grep (file search and reading)
- Bash (date calculation, git log read-only)
- Write (only for creating the work log file)

---

## Execution Procedure

### 1. Parse Arguments

Extract the following information from `$ARGUMENTS`.

| Parameter | Default | Description | Example |
|-----------|---------|-------------|---------|
| Week number | auto-calculated | `W{NN}` format | `W14` |
| Start date | This week's Monday | `YYMMDD` format | `260330` |
| End date | This week's Friday | `YYMMDD` format | `260403` |

If no arguments, auto-calculate based on the current date:

```bash
# This week's Monday (YYMMDD)
date -d "last Monday" +%y%m%d 2>/dev/null || date -v-Mon +%y%m%d

# This week's Friday
date -d "next Friday" +%y%m%d 2>/dev/null || date -v+Fri +%y%m%d

# Week number (ISO week)
date +%V
```

> **Note**: If today is Monday, use `date +%y%m%d` instead of `last Monday`.
> Print the date calculation results for the user to confirm.

Output filename: `docs/work-logs/{start date}-{end date}-W{week number}.md`

---

### 2. Collect Context

Read the following files in order to gather the information needed to determine this week's work.

#### 2-1. PRD (required)

```
docs/temp/local-PRD.md
```

Extract the following information:
- Current phase in progress (P0/P1/P2/P3)
- Incomplete feature requirements for that phase (`FR-P{N}-NN`)
- Completion status of each FR (`[x]` / `[ ]`)
- Estimated effort and BE/FE ownership

#### 2-2. Previous Week's Log (required)

```bash
# Find the most recent week's file
ls -t docs/work-logs/[0-9]*.md | head -1
```

Extract the following information:
- Incomplete items (`[ ]` checkboxes)
- Items explicitly marked for carry-over to next week
- Unresolved blockers

#### 2-3. BACKLOG

```
docs/work-logs/BACKLOG.md
```

Extract the following information:
- Short-term milestone schedule table (items applicable to this week)
- Technical debt items that fit within this week's scope

#### 2-4. Recent Commit History (supplementary)

```bash
git log --oneline -10
```

Review recently completed work to avoid duplicate planning.

---

### 3. Determine Work Plan

Based on the collected information, decide this week's work using the following criteria.

**Priority Determination Criteria**:
1. **Previous week's incomplete carry-over items** — place first
2. **Incomplete FRs for the current phase** — in PRD order
3. **Items from BACKLOG short-term milestones applicable to this week** — refer to schedule table
4. **Items not required this week** — explicitly list items planned for carry-over to next week

**Workload Estimation Criteria**:
- Total work this week = within BE 7 days + within FE 7 days (based on 5 weekdays)
- Refer to estimated effort per FR (as stated in PRD)
- If overloaded, move lower-priority items to "Not Required This Week"

---

### 4. Generate Work Log

Create `docs/work-logs/{filename}.md` using the Write tool.
Follow the structure of `docs/work-logs/WORK-TEMPLATE.md` exactly.

#### File Structure

```markdown
# {start date} - {end date} (W{week number})

> Scope of this file: manages only this week's tasks, blockers, and completed work.
> Long-term planned work goes in [`BACKLOG.md`](./BACKLOG.md); temporary notes go in [`NOTES.md`](./NOTES.md).
>
> **⚠️ Note**: Days 1~5 are for **weekdays (Mon~Fri) only**. Do not include Saturday, Sunday, or holidays in the work plan.

---

## ✅ This Week's Tasks

> **W{N} Position**: {one-line summary of this week's phase and goal}

**[Top Priority — Carried-over or Urgent Items]**

- [ ] [BE/FE] **{FR-ID}** — {task name}
  - {detailed check items}

**[This Week's Tasks]**

- [ ] [BE/FE] **{FR-ID}** — {task name}
  - {detailed check items}

**[Not Required This Week]**

> Items outside this week's scope but worth tracking.

- [ ] {item} ← Carried over to W{next week} (reason)

**[Additional Tasks]**

> Items to tackle if urgent response or early completion of planned tasks.

**[Work Log]**

> Log of actual work performed, separate from the work plan above
> Use this log along with the work plan checklist to compile completed work

---

## ⏳ Blockers

- [ ] {blocker item} (by. assignee)
  - {cause/requirements}

---

## 🏁 Completed Work

> (In progress — to be filled upon completion)

```

#### Writing Quality Criteria

- FR-IDs are referenced directly from the PRD (e.g., `FR-P1-02`)
- Task items are made specific at the "what" level (vague terms like "improve" or "review" are forbidden)
- Previous week's carry-over items are placed in the top-priority section
- Blockers include only unresolved items from PRD and the previous week's log
- The completed work section starts empty (to be filled as the week progresses)

---

### 5. Update README.md

Add the newly created file to the README index.

```bash
# Check current README content
cat docs/work-logs/README.md
```

Add a link to the new week's file in the README (preserve existing format).

---

### 6. Completion Report

```
Work log generated: docs/work-logs/{filename}.md
Week: W{week number} ({start date} ~ {end date})
Collected from: PRD ({N} incomplete FRs) + previous week carry-over ({N} items) + BACKLOG
Task items: top priority {N} / general {N} / planned carry-over {N}
```
