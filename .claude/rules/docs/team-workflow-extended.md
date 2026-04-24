# Agent Team Workflow — Extended Guide

This document contains extended workflow patterns from the core `workflow.md`. See `workflow.md` for the standard 3-phase workflow.

---

## File-Based Communication Structure

```
docs/work-logs/
  TASK.md    ← Manager: task instructions (scope, files, acceptance criteria)
  RESULT.md  ← Executor: task result report (what was done, issues, next steps)
```

**Manager writes TASK.md with:**
- Clear scope (which files to modify)
- Acceptance criteria (how to verify completion)
- Reference materials (existing patterns to follow)

**Executor records in RESULT.md:**
- What was implemented
- Test results
- Any blockers or discovered issues
- Files modified

---

## Subagent Delegation Principles

When delegating work to multiple Haiku agents in parallel:

### Single Responsibility
- Keep scope narrow for each agent
- Separate concerns: exploration / implementation / verification
- Avoid overlap or cross-dependencies

### Isolation Strategy
- Use `isolation: "worktree"` for implementation phases
- Prevents merge conflicts on main branch
- Each agent works in isolated environment

### Recording Results
- Each agent has its own section in RESULT.md
- Document what was done, not what was attempted
- Note any changes to approach or scope

### Count Limits
- **Max 4-5 parallel agents** — beyond that, context cost increases rapidly
- Prioritize tasks with clear dependencies
- Re-consolidate results before next phase

---

## Session Management Timing

| Timing | Action | Agent | Reason |
|--------|--------|-------|--------|
| After implementation phase | `/clear` | Executor | Clear context, prepare for next task assignment |
| After code review | `/compact` | Manager | Maintain design context, reduce token overhead |

**Why `/clear` for executors:**
- Each task is independent; prior context not needed
- Reduces memory overhead for long projects
- Allows fresh perspective on new assignments

**Why `/compact` for managers:**
- Preserves high-level design decisions
- Reduces prompt overhead while retaining critical patterns
- Enables fast replan if scope changes

---

## Common Code Constraints

These constraints apply across all implementation tasks:

- **File size limit:** Files 500 lines or fewer (easier to review, maintain)
- **Python version:** 3.11+ compatibility required
- **Existing patterns:** Follow Key Patterns in `../CLAUDE.md` (don't invent new patterns)
- **No premature generalization:** Implement only what is requested, not future-proof variants

---

## Related Documentation

- [workflow.md](workflow.md) — Standard 3-phase workflow (planning, implementation, verification)
- [critical-rules.md](../critical-rules.md) — Security, error handling, git workflow
