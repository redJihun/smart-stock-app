# Documentation Management

## Directory Structure

```
docs/
  README.md                              # Full document index (required)
  work-logs/                             # Weekly work logs + long-term management documents
    README.md
    BACKLOG.md                           # Long-term planned tasks, tech debt
    NOTES.md                             # Ideas, memos, reference links
    {YYMMDD-start}-{YYMMDD-end}-W{week}.md  # Weekly work log
  architecture-decision-records/         # ADR
    README.md                            # ADR index + status list
    template.md
    {NNNN}-{topic-kebab-case}.md         # Individual ADR
```

## Index to Update When Adding Documents

| Added Document | Index to Update Together |
|---|---|
| ADR (`architecture-decision-records/*.md`) | `architecture-decision-records/README.md` + `docs/README.md` |
| Weekly work log (`work-logs/*.md`) | `work-logs/README.md` |
| General development document (`docs/*.md`) | `docs/README.md` |

## ADR Writing Criteria

Propose writing an ADR if one or more of the following conditions apply:

- A technical decision that is difficult to reverse (library selection, architecture patterns, etc.)
- A decision made after comparing multiple alternatives
- A decision that may look strange when viewed later without context

After adding an ADR, always update both indexes (`architecture-decision-records/README.md`, `docs/README.md`).
