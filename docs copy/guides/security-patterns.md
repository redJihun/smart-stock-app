# Security & Error Handling Patterns

Complete code examples for security rules and error handling patterns referenced in `critical-rules.md`.

---

## Section 1: Security Patterns

### SQL Injection Prevention

#### Safe Patterns (must use)

```python
from sqlalchemy import text

# Named binding
query = text("SELECT * FROM handler WHERE id = :id")
result = session.execute(query, {"id": handler_id})

# text() + in_() usage
from sqlalchemy import in_
status_list = ["active", "pending"]
query = session.query(Handler).filter(Handler.status.in_(status_list))
```

#### Forbidden Patterns

```python
# f-string SQL — absolutely forbidden
query = f"SELECT * FROM handler WHERE id = '{handler_id}'"  # Dangerous!

# String formatting
query = "SELECT * FROM handler WHERE id = '%s'" % handler_id  # Dangerous!
```

### Secret Management

#### Correct Method

```python
# Load from config.yml
from issuance_be_fastapi.config import Config
secret = Config.JWT_SECRET  # Read from environment variable or config.yml
```

#### Pre-commit Check

```bash
git diff --staged | grep -E "(password|secret|token|key)"
# Stop commit if found
```

### Authentication & Authorization

#### Apply authentication to all non-public endpoints

```python
from routers.auth import RequirePermission

@router.post("/work/create")
@RequirePermission()  # Authentication required
async def create_work(
    work_data: WorkSchema,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ...
```

#### Permission Check

```python
if not current_user.has_permission("work.create"):
    raise HTTPException(status_code=403, detail="Insufficient permission")
```

### Input Validation

#### Validate in Pydantic Schema

```python
from pydantic import BaseModel, Field, validator

class WorkSchema(BaseModel):
    work_no: str = Field(..., min_length=1, max_length=50)
    handler_count: int = Field(ge=1, le=999)

    @validator('work_no')
    def validate_work_no(cls, v):
        if not v.isalnum():
            raise ValueError("work_no must be alphanumeric")
        return v

    class Config:
        orm_mode = True
```

#### Additional Validation in Router

```python
if work_data.handler_count > 10:
    raise HTTPException(status_code=400, detail="Exceeded max handler count")
```

### External Call Safety

#### Timeout Setting Required

```python
import requests
response = requests.get(url, timeout=5)  # 5 second limit

# When using asyncio
asyncio.wait_for(async_func(), timeout=5)
```

#### SSL Verification

```python
# Production: SSL verification by default (https://...)
response = requests.get("https://api.example.com/...")

# Even in dev environments, handle self-signed certs properly
import certifi
response = requests.get(url, verify=certifi.where())
```

---

## Section 2: Error Handling Patterns

### CRUD & Router Error Boundary

#### CRUD Functions (domain/)

```python
def get_handler_info(session: Session, handler_id: str) -> HandlerInfo:
    result = session.query(HandlerInfo).filter(...).first()
    if not result:
        raise ValueError(f"Handler {handler_id} not found")
    return result
```

#### Router Functions (routers/)

```python
@router.get("/handler/{id}")
async def get_handler(id: str, db: Session = Depends(get_db)):
    try:
        handler = get_handler_info(db, id)
        logger.info(f"Handler retrieved: {id}")
        return {"result": "OK", "data": handler}
    except ValueError as e:
        logger.warning(f"Invalid handler: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
```

### Response Format (Consistency)

```python
# Success
{"result": "OK", "data": {...}}

# Error
{"result": "ERROR", "error": "message"}

# Never use "SUCCESS" — always "OK"
```

### Database Error Handling

```python
from sqlalchemy.exc import IntegrityError, OperationalError

try:
    session.add(new_record)
    session.commit()
except IntegrityError:
    session.rollback()
    logger.warning(f"Duplicate key or constraint violation")
    raise HTTPException(status_code=400, detail="Data conflict")
except OperationalError:
    session.rollback()
    logger.error(f"Database connection lost")
    raise HTTPException(status_code=503, detail="Service unavailable")
```

---

## Related Documentation

- `critical-rules.md` — Rule definitions and checklists
- `issuance-fastapi/.claude/rules/code-rules.md` — Additional patterns for Python/FastAPI
