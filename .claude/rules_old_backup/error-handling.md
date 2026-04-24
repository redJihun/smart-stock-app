# Error Handling Rules

## Logging Level Criteria

| Level | When to Use | Example |
|-------|------------|---------|
| DEBUG | HTTP request/response | `logger.debug(f"GET /handler/{id}")` |
| INFO | Task completion | `logger.info("Session created: ssi_20250325")` |
| WARNING | Expected failure, partial success | `logger.warning("Handler offline, retrying...")` |
| ERROR | Unexpected failure | `logger.error(f"DB connection failed: {e}")` |

## CRUD ↔ Router Error Boundary

### CRUD Functions (domain/)
- **Exception propagation**: Propagate SQLAlchemy errors as-is
- **Validation errors**: Raise `ValueError`, `KeyError`
- **Logging**: Use only DEBUG/WARNING when needed

```python
def get_handler_info(session: Session, handler_id: str) -> HandlerInfo:
    result = session.query(HandlerInfo).filter(...).first()
    if not result:
        raise ValueError(f"Handler {handler_id} not found")
    return result
```

### Router Functions (routers/)
- **Wrap CRUD calls with try-except**
- **Unified response**: `{"result": "OK", "data": ...}` or `{"result": "ERROR", "error": ...}`
- **Logging**: Record at INFO/WARNING/ERROR levels

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

## HTTP Status Codes

| Situation | Code | Example |
|-----------|------|---------|
| Success | 200 | Data returned successfully |
| Invalid input | 400 | Required field missing |
| Unauthenticated | 401 | No token |
| Unauthorized | 403 | Insufficient permissions |
| Resource not found | 404 | Handler ID not found |
| Server error | 500 | Unexpected error |

## Response Format (Consistency)

```python
# Success
{"result": "OK", "data": {...}}

# Error
{"result": "ERROR", "error": "message"}

# Never use "SUCCESS" — always "OK"
```

## Database Error Handling

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
