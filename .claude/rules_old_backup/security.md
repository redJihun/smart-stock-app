# Security Rules

## SQL Injection Prevention

### Safe Patterns (must use)
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

### Forbidden Patterns
```python
# f-string SQL — absolutely forbidden
query = f"SELECT * FROM handler WHERE id = '{handler_id}'"  # Dangerous!

# String formatting
query = "SELECT * FROM handler WHERE id = '%s'" % handler_id  # Dangerous!
```

## Secret Management

### Never include in code
- DB passwords, API keys, JWT secrets
- e.g.: `password = "mysql123"`

### Correct method
```python
# Load from config.yml
from issuance_be_fastapi.config import Config
secret = Config.JWT_SECRET  # Read from environment variable or config.yml
```

### Pre-commit check
```bash
git diff --staged | grep -E "(password|secret|token|key)"
# Stop commit if found
```

## Authentication & Authorization

### Apply authentication to all non-public endpoints

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

### Permission check
```python
if not current_user.has_permission("work.create"):
    raise HTTPException(status_code=403, detail="Insufficient permission")
```

## Input Validation

### Validate in Pydantic schema
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

### Additional validation in router
```python
if work_data.handler_count > 10:
    raise HTTPException(status_code=400, detail="Exceeded max handler count")
```

## External Call Safety

### Timeout setting required
```python
import requests
response = requests.get(url, timeout=5)  # 5 second limit

# When using asyncio
asyncio.wait_for(async_func(), timeout=5)
```

### SSL verification
```python
# Production: SSL verification by default (https://...)
response = requests.get("https://api.example.com/...")

# Even in dev environments, handle self-signed certs properly
import certifi
response = requests.get(url, verify=certifi.where())
```

## Pre-Deploy Checklist

- [ ] f-string SQL removed (`text()` + binding confirmed)
- [ ] No hardcoded secrets (config.yml verified)
- [ ] All API endpoints have `@RequirePermission()` or explicitly marked public
- [ ] Input validation complete (Pydantic + router)
- [ ] No sensitive information exposed in error responses
