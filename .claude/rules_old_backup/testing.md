# Testing Rules

## Test Structure

```
tests/
  conftest.py           # Global fixtures (db_session, app, client)
  test_*.py            # Test files (per module)
  integration/
    test_*.py          # Integration tests (real DB, API)
  unit/
    test_*.py          # Unit tests (mocking)
```

## AAA Pattern (Arrange-Act-Assert)

```python
def test_get_handler_info_success(db_session):
    # Arrange: Set up test data
    handler = HandlerInfo(
        id="HDL001",
        name="Handler 1",
        status="active"
    )
    db_session.add(handler)
    db_session.commit()

    # Act: Execute function
    result = get_handler_info(db_session, "HDL001")

    # Assert: Verify result
    assert result.id == "HDL001"
    assert result.name == "Handler 1"
```

## Test Isolation (TDD Principles)

### Database isolation
```python
@pytest.fixture
def db_session():
    """Independent DB session for each test"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
```

### No cross-test interference
- Each test uses independent data
- No shared resources (files, environment variables, etc.)
- Tests can run in any order

## Mock Usage Criteria

### Use Mock (unit tests)
```python
from unittest.mock import patch

def test_send_notification():
    # Use Mock instead of calling external API
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200

        result = send_notification("test@example.com")

        assert result == True
        mock_post.assert_called_once()
```

### Use real DB (integration tests)
```python
def test_create_handler_integration(db_session):
    # Save to real DB and query
    handler = create_handler_info(db_session, "HDL001", "Handler 1")

    result = session.query(HandlerInfo).filter_by(id="HDL001").first()
    assert result.id == "HDL001"
```

## Test Naming Convention

```python
def test_{function_name}_{scenario}():
    """Test a specific scenario of a specific function"""
    pass

# Examples
def test_get_handler_info_success():  # ✓
def test_get_handler_info_not_found():  # ✓
def test_create_session_with_invalid_data():  # ✓

def test_handler():  # ✗ (too vague)
def test_works():  # ✗ (what is being tested?)
```

## Coverage Criteria

| Type | Criteria | Target |
|------|----------|--------|
| Business logic | 80% or above | Required |
| API routers | 70% or above | Recommended |
| Utilities | 60% or above | Recommended |
| Schema validation | 90% or above | Recommended |

### Check coverage
```bash
uv run pytest --cov=issuance_be_fastapi tests/
```

## Running Tests

### All tests
```bash
uv run pytest tests/ -v
```

### Specific test file
```bash
uv run pytest tests/test_handler.py -v
```

### Specific test function
```bash
uv run pytest tests/test_handler.py::test_get_handler_info_success -v
```

### Failed tests only
```bash
uv run pytest tests/ -v --lf
```

## Fixture Writing Criteria

### 1. Fixtures needed by all tests → conftest.py
```python
@pytest.fixture
def db_session():
    """Global DB session fixture"""
    pass

@pytest.fixture
def client(db_session):
    """Global test client"""
    pass
```

### 2. Fixtures needed by specific tests only → respective file
```python
@pytest.fixture
def handler_data():
    """Used only in test_handler.py"""
    return {"id": "HDL001", "name": "Handler 1"}
```

## Important Notes

- Tests must be committed together with production code
- Red flag: never merge code without passing tests
- When modifying legacy code, write tests first (reproduce the defect)
- Remove temporary tests (.skip) before committing
