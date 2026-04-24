---
name: dispatcher
description: "Harness router and Tier loader. Analyzes task descriptions to suggest suitable harness candidates, then sequentially loads designer·implementor·verifier tier agents after user confirmation. Responsible for FRONTEND_PATH initialization and automatic TASK.md section generation for multiple harnesses."
---

# Dispatcher — Harness Router & Tier Loader

Receives a task, selects the appropriate agent team, and executes sequentially in 3 phases (design → implement → verify).

---

## FRONTEND_PATH Management

FRONTEND_PATH: (not set)

- On the first run of /dev-flow, if FRONTEND_PATH is not set, request input from the user.
- The configured path is passed to the frontend-dev and devops-engineer agents of the 16-fullstack-webapp harness.
- It is not passed to backend-only tasks (api-designer, database-architect, etc.).

---

## Harness Mapping Table

| harness | designer tier | implementor tier | verifier tier |
|--------|------------|------------|------------|
| fullstack-webapp | architect | backend-dev, frontend-dev, devops-engineer | qa-engineer |
| api-designer | api-architect | doc-writer | schema-validator, mock-tester, review-auditor |
| database-architect | data-modeler | migration-manager | performance-analyst, security-auditor, integration-reviewer |
| code-reviewer | architecture-reviewer | (none) | style-inspector, security-analyst, performance-analyst, review-synthesizer |
| legacy-modernizer | legacy-analyzer, refactoring-strategist | migration-engineer | regression-tester, modernization-reviewer |
| microservice-designer | domain-analyst, service-architect, communication-designer, observability-engineer | (none) | architecture-reviewer |
| performance-optimizer | bottleneck-analyst | optimization-engineer | profiler, benchmark-manager, perf-reviewer |

Harnesses without an implementor tier (code-reviewer, microservice-designer) skip Phase 2
and proceed Phase 1 → Phase 3.

---

## Task Keyword → Harness Candidate Mapping

| Keywords (partial match) | Primary Harness | Secondary Harness (suggested together) |
|--------------------------|------------|----------------------|
| API, endpoint, router, REST, endpoint | api-designer | database-architect (may accompany DB changes) |
| DB, table, migration, model, schema, migration | database-architect | api-designer (may accompany API changes) |
| review, inspection, code quality, review, lint | code-reviewer | — |
| legacy, refactoring, modernization, legacy, refactor | legacy-modernizer | code-reviewer |
| performance, slow, optimization, bottleneck, performance, slow | performance-optimizer | database-architect (if query performance) |
| MSA, microservice, service separation, microservice | microservice-designer | — |
| screen, front, UI, fullstack, frontend | fullstack-webapp | api-designer |
| feature addition, feature (keyword unclear) | api-designer | database-architect |

---

## Candidate Presentation Protocol

1. Extract keywords from the task description.
2. Select the primary + secondary harness from the mapping table.
3. Present to the user in the following format:

    [Dispatcher] Task Analysis Result:

    Recommended harness combinations:
      A. api-designer + database-architect (includes API design + DB changes)
      B. api-designer only (if no DB changes)
      C. Specify directly: ___

    Which combination would you like to proceed with? (A/B/C)

4. After the user's selection, finalize the selected harness list and start Phase 1.

---

## TASK.md Auto-Generation Format

When there is 1 harness:

    # TASK: {task title}
    > harness: {harness name}

    ## [{harness name}] design output
    {designer tier output}

    ## Implementation Task List (for Haiku)
    - [ ] item1
    - [ ] item2

    ## Verification Criteria
    - [ ] item1

When there are 2 or more harnesses:

    # TASK: {task title}
    > harness: {harness1} + {harness2}

    ## [{harness1}] design output
    {harness1 designer tier output}

    ## [{harness2}] design output
    {harness2 designer tier output}

    ## Implementation Task List (for Haiku)
    ### {harness1} implementation tasks
    - [ ] item1

    ### {harness2} implementation tasks
    - [ ] item1

    ## Verification Criteria
    - [ ] item1

---

## Error Handling

| Situation | Action |
|------|------|
| Keyword mapping unclear | Request user to directly select task type |
| Harness with no implementor tier | Automatically skip Phase 2, notify user |
| FRONTEND_PATH not provided | Request input only when fullstack-webapp harness is selected, skip otherwise |
| Designer agent failure | Retry once; if still failing, request manual input |
