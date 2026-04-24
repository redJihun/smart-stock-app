# Documentation Structure

Standard directory structure for all repositories in the workspace.

## Directory Layout

```
docs/
  README.md                              # Full document index (required)
  work-logs/                             # Weekly work logs + long-term management documents
    README.md
    BACKLOG.md                           # Long-term planned tasks, tech debt
    NOTES.md                             # Ideas, memos, reference links
    {YYMMDD-start}-{YYMMDD-end}-W{week}.md  # Weekly work log
  guides/                                # Feature guides and setup
    README.md                            # Guides index
    *.md                                 # Individual guides
  architecture-decision-records/         # ADR
    README.md                            # ADR index + status list
    template.md
    {NNNN}-{topic-kebab-case}.md         # Individual ADR
```

## When to Create Each Type

| Type | When | Update Index |
|------|------|---|
| ADR | Technical decision, difficult to reverse | `architecture-decision-records/README.md` |
| Weekly work log | End of week summary | `work-logs/README.md` |
| Guide | Feature setup, procedural documentation | `guides/README.md` |
| BACKLOG | Long-term tech debt items | Keep updated as discovered |
| NOTES | Ideas, research links, memos | Keep updated as needed |
