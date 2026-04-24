---
name: close-work-log
description: Reads [x] items and work log from the weekly work log and auto-fills the 'Completed Work' section
allowed-tools: ["Read", "Glob", "Bash", "Edit"]
model: sonnet
---

# /close-work-log — Weekly Work Log Completion Section Filler

## Role Definition

You are the **organizer** responsible for closing out a weekly work log.
Read the `[x]` checked items and the `[Work Log]` section from the target week's file and automatically write the `## 🏁 Completed Work` section.

Strictly prohibited:
- Modifying code files (editing other files is forbidden)
- git commit, git push
- Modifying any part of the file other than the `## 🏁 Completed Work` section

Allowed:
- Read (reading work log files)
- Glob, Bash (file search)
- Edit (modifying only the `## 🏁 Completed Work` section)

---

## Execution Procedure

### 1. Parse Arguments

Extract the file path from `$ARGUMENTS`.

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `{file path}` | - | Path to the target week's log | `docs/work-logs/260330-260403-W14.md` |

**When no argument provided**: automatically select the most recent week's file:

```bash
ls -t docs/work-logs/[0-9]*.md | head -1
```

---

### 2. Read File and Classify Items

Read the entire target file with Read and classify the following:

1. **`[x]` checked items** → completed items (preserve section group information)
2. **`[ ]` unchecked items** → incomplete/carried-over items (include explicit carry-over to next week)
3. **`-` line items in the `[Work Log]` section** → actual work records
4. **`~~...~~` strikethrough items** → cancelled/decided items (handle separately)

---

### 3. Write Completed Work Content

Generate the section content according to the following rules:

#### Rule 1: Preserve Top-Level Groups
Preserve the top-level group structure from the original file (`**[Top Priority ...]**`, `**[This Week's Tasks]**`, etc.) and group only the `[x]` items within them.

#### Rule 2: Include Sub-Details
For each completed item, include the original `-` sub-list items (sub-details, technical details, etc.) exactly as they appear.

**Example:**
```
- [BE+FE] **FR-P1-02** — PGM (project) create/edit/delete UI complete
  - BE: POST /projects/ request schema ↔ FE form field mapping confirmed
  - BE: DELETE /projects/{id} → 409 block applied when WorkInfo is referenced
  - FE: PGM register/edit/delete modal and dialog implemented
  - FE: Register, edit, delete buttons added to list/detail screens
```

#### Rule 3: Merge Work Log
Process the line items from the `[Work Log]` section as follows:
- If a related planned item exists → merge under that item's sub-details
- If no related item exists → classify under a new group **[Bug Fixes & Improvements]** or **[Docs & Misc]**

**Example:**
```
**[Bug Fixes & Improvements]**

- Profile edit modal — name not reflected + description caching bug fixed (2026-04-02)
- User edit/delete malfunction bug fixed (2026-04-01)
```

#### Rule 4: Incomplete/Carried-Over Items
`[ ]` unchecked items:
- Mark with `⚠️` and place in the **[In Progress / Incomplete]** group
- Items explicitly marked "carry over to W{next week}" go in a separate **[Carried over to W{N+1}]** group

**Example:**
```
**[In Progress / Incomplete]**

- ⚠️ [FE] Page load error after PGM edit (in progress)
  - Mapped variable error needs investigation

**[Carried over to W15]**

- FR-P1-06 KMS → in-house BE auth migration (FE 5~7 day large-scale task)
```

#### Rule 5: Strikethrough Items
`~~...~~` strikethrough items and their `**(Decision)**` notes below them are merged and recorded at the end of the completed work section.

---

### 4. Replace Section

Use the Edit tool to replace the existing placeholder in the `## 🏁 Completed Work` section with the content written in step 3.

**Target to replace:**
```
old_string:
> (In progress — to be filled upon completion)

new_string:
{completed work content written in step 3}
```

---

## Completion Report

```
Completed work section updated: docs/work-logs/{filename}.md
Completed items: {N}
Incomplete/carried over: {N}
Work log reflected: {N} entries
```

---

## Expected Final Result

When `/close-work-log` or `/close-work-log docs/work-logs/260330-260403-W14.md` is run:
- The `## 🏁 Completed Work` section of the target week's file is automatically filled in
- `[x]` items are organized in completed form while preserving their original groups
- Work log items are merged into related groups
- Incomplete/carried-over items are also recorded at the bottom of the section with ⚠️ markers

**Example result structure:**
```
## 🏁 Completed Work

**[Carried over from W13]**

- [FE] **User creation duplicate-check logic** — API connection and validation complete
  - POST /auth/users/ 409 response parsing
  - FE duplicate notification message integration complete (2026-04-01)

**[P1 Key Features]**

- [BE+FE] **FR-P1-02** — PGM create/edit/delete UI complete
  - BE: POST /projects/ request schema ↔ FE form field mapping confirmed
  - ...

**[Bug Fixes & Improvements]**

- Profile edit modal bug fixed (2026-04-02)
- ...

**[In Progress / Incomplete]**

- ⚠️ [FE] Page load error after PGM edit (in progress)

**[Carried over to W15]**

- FR-P1-06 KMS → in-house BE auth migration
```
