# Code Quality Rules

## File Size Limit
- **Maximum 500 lines** — split if exceeded (by class/module)
- Reason for exceeding: insufficient separation of concerns, difficulty in testing

## Function Size
- **Maximum 50 lines** (excluding docstring, including blank lines)
- Exception: discuss cases with complex queries or many constant declarations

## Naming Rules

| Target | Rule | Example |
|--------|------|---------|
| Function | snake_case | `get_handler_info()` ✓ |
| Class | PascalCase | `HandlerSchema` ✓ |
| Constant | UPPER_SNAKE | `MAX_RETRY = 3` ✓ |
| Variable | snake_case | `session_id` ✓ |

## Early Return Pattern

```python
# ✓ Good
if not condition:
    return error_response()
process()

# ✗ Avoid
if condition:
    process()
else:
    return error_response()
```

## Complexity Management

- **Use the simplest expressions possible** — ternary operators must fit on one line
- **Maximum loop depth of 3 levels** — extract into a function if deeper
- **Maximum 5 conditionals** — use early return or helper functions if exceeded

## Boilerplate Reuse

Follow Key Patterns in CLAUDE.md:
- CRUD router: `routers/workinfos.py`
- ORM model: `domain/board/models.py` (use `SeqUidRuleMixin`)
- Pydantic schema: `domain/board/schemas.py` (`orm_mode = True`)
