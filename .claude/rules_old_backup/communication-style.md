# Communication Style

## Core Principles

- **Conciseness**: No need for summaries or re-explanations (the user can read the code)
- **Korean-oriented**: Keep technical terms and code in their original language
- **Action-oriented**: Focus on "what was done"

## Response Structure

### 1. Action Result (1-2 sentences)
```
Added 2 CRUD APIs. (concise)

✗ I added CRUD APIs, which are for Create, Read, Update, Delete operations. (re-explanation)
```

### 2. Summary When Needed
- List of modified files (can be omitted if diff is available)
- Test results
- Cause + solution when a problem occurs

### 3. Next Steps (optional)
- Only when the user's decision is needed
- Present options and recommendations

## Error Reporting Format

### Error Encountered
```
[Error 404] Handler not found in database
File: domain/board/crud/handler.py:45
```

### Cause Analysis
```
→ query().filter(Handler.id == handler_id).first() returns None
→ Handler ID does not exist in DB or condition error
```

### Solution
```
1. Add exception handling to get_handler_info() function
2. Verify test data
```

## Code Reference Format

File path + line number:
```
routers/dashboard.py:23 — get_recent_alerts function
```

## Accepting Negative Feedback

Regarding user feedback:
- Correct immediately without explaining reasons
- "The reason I didn't change that part is..." ✗ (defensive)
- "Fixed." ✓ (action-oriented)

## Korean Grammar

- Use polite form (friendliness)
- Use past tense for completed actions (completion tense)
- Maintain consistency (no mixing)

## Document Writing

- Use markdown (code blocks, tables, lists)
- Documents and memory in Korean + technical terms in original language
- File paths: use exact paths like `docs/`, `issuance_be_fastapi/`, etc.

## Expressions to Avoid

- "Now you can ~" (stating the obvious)
- "This was a complex/difficult task" (meaningless)
- "We should ~ in the future" (not confirmed)
