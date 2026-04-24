---
name: command-gen
description: Generate new Claude Code commands in a consistent format
allowed-tools: ["Read", "Glob", "Write"]
model: sonnet
---

# /command-gen — Command Generation Skill

## Purpose

Based on the information provided by the user, generate a new command file in `.claude/commands/`.
Analyze existing command patterns to maintain a consistent format.

## Input Format

/command-gen name=<command-name> purpose=<purpose> [model=haiku|sonnet] [tools=Tool1,Tool2,...]

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `name` | ✓ | Command file name (kebab-case) | `name=db-check` |
| `purpose` | ✓ | Purpose/role of the command | `purpose=Check DB connection status` |
| `model` | - | Execution model (default: haiku) | `model=sonnet` |
| `tools` | - | Allowed tools list (default: Bash,Read) | `tools=Bash,Read,Write` |

Natural language input without parameter format is also accepted:
/command-gen Create a db-check command that checks DB connection status

## Execution Procedure

### 1. Input Parsing

Extract the following from $ARGUMENTS:
- **name**: Command file name (infer from purpose if absent, convert to kebab-case)
- **purpose**: Role/purpose of the command
- **model**: `haiku` or `sonnet` (default: `haiku`)
- **tools**: Allowed tools array (default: `["Bash", "Read"]`)

**Automatic Model Selection Criteria** (when not specified):
- `haiku`: listing bash commands, running validation, generating boilerplate, analyzing documents
- `sonnet`: analyzing context, making code design judgments, includes multi-step decision-making

### 2. Reference Existing Commands

Read one existing command most similar in purpose using Read, and reference its body structure:

| Purpose Type | Reference Command |
|--------------|------------------|
| Code validation/inspection | `.claude/commands/verify.md` |
| Code/file generation | `.claude/commands/crud-gen.md` |
| Task planning/analysis | `.claude/commands/task-plan.md` |
| Deployment/operations check | `.claude/commands/deploy-check.md` |
| Message/document writing | `.claude/commands/commit-message-suggest.md` |

If the purpose is unclear or does not match any entry, skip the reference and use Structure A by default.

### 3. Body Structure Selection

Choose one of two structures based on purpose:

**Structure A (procedural)** — bash command-oriented, suitable for `model: haiku`:
```
# /{name} — {one-line description}

## Purpose
{purpose description}

## Execution Steps

### 1. {step name}
{bash command or description}

### 2. {step name}
...

## Result Summary
{output format example}
```

**Structure B (role-definition)** — includes analysis/judgment, suitable for `model: sonnet`:
```
# /{name} — {one-line description}

## Role Definition

{role description}

Strictly prohibited:
- ...

Allowed:
- ...

## Execution Procedure

### 1. {step name}
...

## Completion Report
{output format example}
```

**Structure Selection Criteria**:
- `model: haiku` → Structure A
- `model: sonnet` + includes analysis/judgment → Structure B

### 4. Generate Command File

Create `.claude/commands/{name}.md` using the Write tool with the following frontmatter:

```yaml
---
name: {name}
description: {one-line summary of purpose in English}
allowed-tools: {tools JSON array}
model: {model}
---
```

Then write the body using the chosen structure (A or B).

**Writing Quality Criteria**:
- Always use the `$ARGUMENTS` placeholder at the point where user input is referenced
- Wrap bash commands in code blocks
- Present output/result format as an example
- No vague expressions ("process it" → "run ruff check and list error lines")
- Before creating the file, verify for duplicates with `Glob(".claude/commands/{name}.md")`

### 5. Completion Report

After generation is complete, output in the following format:

```
Command created: .claude/commands/{name}.md
Model: {model}
Allowed tools: {tools}
Structure: {A(procedural) or B(role-definition)}
Usage: /{name} {input example}
```

---

## Expected Final Result

When `/command-gen name=db-check purpose=Check DB connection status` is run:
- `.claude/commands/db-check.md` is created
- frontmatter: includes `name`, `description`, `allowed-tools`, `model`
- body: written in procedural style (Structure A) with bash commands
- Same format as existing commands is maintained

## Verification Criteria

- [ ] `.claude/commands/command-gen.md` file is created
- [ ] frontmatter contains all 4 fields: `name`, `description`, `allowed-tools`, `model`
- [ ] `$ARGUMENTS` placeholder exists in the body
- [ ] Input parameter table (name/purpose/model/tools) is included
- [ ] Structure A / Structure B selection criteria are specified
- [ ] Completion report output format is specified
- [ ] Duplicate check (Glob) step is included
