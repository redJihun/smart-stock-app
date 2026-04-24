---
name: dev-flow
description: "7-harness-based development flow orchestrator. Selects the agent team matching the task type via dispatcher, and executes design (Phase 1) → implementation (Phase 2) → verification (Phase 3) in order. Use for all development tasks such as 'create a new feature', 'add an API', 'change DB', 'code review', 'performance improvement', etc."
---

# /dev-flow — Development Flow Orchestrator

Input a task and it selects the appropriate agent team to execute design→implementation→verification in order.

---

## Execution Flow

    /dev-flow "task description"
             ↓
    [Phase 0] Check FRONTEND_PATH + dispatcher presents harness candidates → (user confirmation)
             ↓
    [Phase 1] Designer tier runs → temp/TASK.md generated
             ↓ (user approves TASK.md)
    [Phase 2] Implementor tier runs (Haiku recommended) → temp/RESULT.md generated
             ↓
    [Phase 3] Verifier tier runs → verification report
             ↓
    Manager commit decision

---

## Phase 0: Initialization & Harness Selection

1. Check FRONTEND_PATH in dispatcher.md: if not set and the selected harness includes fullstack-webapp, prompt for path input
2. Load `.claude/agents/dispatcher.md`
3. Pass the task description to the dispatcher to present harness candidates
4. Confirm the harness list after user approval

---

## Phase 1: Design (designer tier)

Load the designer tier agent for each selected harness.

| Harness | Agent path to load |
|--------|-------------------|
| fullstack-webapp | .claude/16-fullstack-webapp/.claude/agents/architect.md |
| api-designer | .claude/18-api-designer/.claude/agents/api-architect.md |
| database-architect | .claude/19-database-architect/.claude/agents/data-modeler.md |
| code-reviewer | .claude/21-code-reviewer/.claude/agents/architecture-reviewer.md |
| legacy-modernizer | .claude/22-legacy-modernizer/.claude/agents/legacy-analyzer.md + refactoring-strategist.md |
| microservice-designer | .claude/23-microservice-designer/.claude/agents/ domain-analyst.md + service-architect.md + communication-designer.md + observability-engineer.md |
| performance-optimizer | .claude/29-performance-optimizer/.claude/agents/bottleneck-analyst.md |

Output: temp/TASK.md (using the TASK.md auto-generation format from dispatcher)

Wait for user approval: review TASK.md, then reply "proceed" or request changes

---

## Phase 2: Implementation (implementor tier)

Harnesses without an implementor tier (code-reviewer, microservice-designer) skip this phase.
When skipping, notify the user: "[{harness name}] No implementor tier — proceeding to Phase 3."

Load the implementor tier agent for each selected harness.

| Harness | Agent path to load |
|--------|-------------------|
| fullstack-webapp | .claude/16-fullstack-webapp/.claude/agents/backend-dev.md + frontend-dev.md + devops-engineer.md |
| api-designer | .claude/18-api-designer/.claude/agents/doc-writer.md |
| database-architect | .claude/19-database-architect/.claude/agents/migration-manager.md |
| legacy-modernizer | .claude/22-legacy-modernizer/.claude/agents/migration-engineer.md |
| performance-optimizer | .claude/29-performance-optimizer/.claude/agents/optimization-engineer.md |

Execution model: Haiku recommended (implementation based on already-designed TASK.md)
Output: temp/RESULT.md

---

## Phase 3: Verification (verifier tier)

Load the verifier tier agent for each selected harness.

| Harness | Agent path to load |
|--------|-------------------|
| fullstack-webapp | .claude/16-fullstack-webapp/.claude/agents/qa-engineer.md |
| api-designer | .claude/18-api-designer/.claude/agents/ schema-validator.md + mock-tester.md + review-auditor.md |
| database-architect | .claude/19-database-architect/.claude/agents/ performance-analyst.md + security-auditor.md + integration-reviewer.md |
| code-reviewer | .claude/21-code-reviewer/.claude/agents/ style-inspector.md + security-analyst.md + performance-analyst.md + review-synthesizer.md |
| legacy-modernizer | .claude/22-legacy-modernizer/.claude/agents/regression-tester.md + modernization-reviewer.md |
| microservice-designer | .claude/23-microservice-designer/.claude/agents/architecture-reviewer.md |
| performance-optimizer | .claude/29-performance-optimizer/.claude/agents/ profiler.md + benchmark-manager.md + perf-reviewer.md |

Output: verification report (inline response)
When the verifier finds a required fix: re-call the corresponding implementor agent → fix → re-verify (max 2 cycles)

---

## Agent Composition

| Agent | File | Role |
|---------|------|------|
| dispatcher | .claude/agents/dispatcher.md | harness selection, tier loading, TASK.md generation |

---

## Usage Examples

    /dev-flow "Add session query API and add index to sessions table"
    → dispatcher: recommends api-designer + database-architect
    → Phase 1: api-architect + data-modeler design
    → Phase 2: doc-writer + migration-manager implement (Haiku)
    → Phase 3: schema-validator + security-auditor + integration-reviewer verify

    /dev-flow "Do a full code review"
    → dispatcher: recommends code-reviewer
    → Phase 1: architecture-reviewer designs (report)
    → Phase 2: skipped (no implementor)
    → Phase 3: style-inspector, security-analyst, performance-analyst, review-synthesizer verify

    /dev-flow "Session query response is slow"
    → dispatcher: recommends performance-optimizer + database-architect
    → Phase 1: bottleneck-analyst + data-modeler analyze bottleneck
    → Phase 2: optimization-engineer + migration-manager optimize
    → Phase 3: profiler + benchmark-manager + performance-analyst verify

---

## Error Handling

| Situation | Handling |
|------|------|
| No task description | Ask "What would you like to work on?" then restart |
| User requests TASK.md changes | Re-call designer agent and regenerate TASK.md |
| Phase 2 failure | List failed items in RESULT.md, treat as unimplemented in Phase 3 |
| Verifier finds a required fix | Re-call the corresponding implementor agent → fix → re-verify (max 2 cycles) |
