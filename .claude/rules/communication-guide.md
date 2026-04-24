# Communication Guide

Defines effective interaction with Claude and team communication practices.

---

## Core Principles

### Clarity & Conciseness
- **Define intent clearly:** Explicitly state task purpose and desired outcome
- **Avoid redundancy:** Omit unnecessary explanations (users can read code)
- **Break complex tasks into steps:** Decompose large work into manageable pieces

### Action-Oriented
- **Lead with impact:** Start with what was accomplished (1-2 sentences)
- **Focus on results:** Report outcomes, not process
- **Accept feedback:** Respond immediately to corrections without justification

### Language Conventions
- **Preserve technical terms:** Keep code, libraries, and technical names in English
- **Use imperative tone:** Direct, clear phrasing
- **Complete actions:** Use past tense for reporting ("Implemented X" not "Implementing X")

---

## 6 Core Communication Principles

1. **Be Specific and Detailed** — Define desired outcome precisely (see [communication-patterns.md](../../docs/guides/communication-patterns.md) for examples)
2. **Use Examples** — Provide reference format/style when applicable
3. **Break Complex Tasks into Steps** — Decompose large work into smaller phases
4. **Encourage Step-by-Step Thinking** — Guide logical progression
5. **Iterate with Feedback** — Refine incrementally based on input
6. **Provide Full Context** — Include all necessary background for each request

See [communication-patterns.md](../../docs/guides/communication-patterns.md) for detailed examples and checklists.

---

## Response Structure

### 1. Action Result (1-2 sentences)
Express task completion concisely without terminology explanation.

### 2. Summary When Needed
- Modified file list
- Test results
- Issues encountered: root cause + resolution

### 3. Next Steps (optional)
- Present only when user decision is needed
- Provide options and recommendations

See [communication-patterns.md](../../docs/guides/communication-patterns.md) § Response Structure for detailed examples.

---

## Error Reporting Format

**3-Step Structure:**
1. **Error Encountered** — [Error code] + file path + line number
2. **Cause Analysis** — Trace root cause (use arrow notation: → arrow)
3. **Solution** — Provide verifiable fix

See [communication-patterns.md](../../docs/guides/communication-patterns.md) § Error Reporting Format for examples.

---

## Code & Document References

### Code Reference Format
Include file path and line number: `routers/dashboard.py:23 — get_recent_alerts function`

### Document Writing
- Use Markdown (code blocks, tables, lists)
- Preserve technical terms in English
- Use exact file paths

---

## Writing Conventions

### Active Voice & Tense
- Use imperative/past tense for actions ("Fixed X" not "Fixing X")
- Report facts without hedging
- Avoid speculation about future requirements

### Accepting Feedback
- Respond immediately to corrections
- Do not explain why feedback wasn't implemented
- Keep responses brief ("Done." is sufficient)

### Avoid These Patterns
- "Now you can..." (states the obvious)
- "This is complex/difficult" (adds no value)
- "We should..." for unverified claims

---

## Task-Specific Guidance

- **Content Creation** — Specify audience, tone, and structure
- **Document Summary & Q&A** — Clarify focus, questions, and citation preferences
- **Data Analysis** — Define output format and metrics
- **Brainstorming** — Specify quantity, types, and categorization

See [communication-patterns.md](../../docs/guides/communication-patterns.md) § Task-Specific Guidance for checklists.

---

## Quality & Accuracy

**Minimize Hallucinations:**
1. Acknowledge uncertainty ("If unsure, let me know")
2. Decompose complex tasks (one step per turn)
3. Request clarification when context is incomplete

See [communication-patterns.md](../../docs/guides/communication-patterns.md) § Troubleshooting Strategies for detailed approaches.

---

## Related Documents

- [critical-rules.md](critical-rules.md) — Security, error handling, git workflow
- [workflow.md](workflow.md) — Team collaboration patterns
- [docs/guides/communication-patterns.md](../../docs/guides/communication-patterns.md) — Examples, patterns, and detailed guidance
