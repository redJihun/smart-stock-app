# Critical Rules (Layer 1)

This file consolidates the most critical rules that apply across all repositories in the workspace. All developers must follow these rules without exception.

- **Layer 1 (Critical)**: All repos apply these rules
- **Layer 2 (Repository-specific)**: Applied per repository
- **Layer 3 (Team-specific)**: Applied to specific teams or workflows

---

## Section 1: Security

### SQL Injection Prevention

#### Safe Patterns (must use)
See `docs/guides/security-patterns.md` § SQL Injection Prevention for safe pattern examples.

#### Forbidden Patterns
See `docs/guides/security-patterns.md` § SQL Injection Prevention for forbidden pattern examples.

### Secret Management

#### Never include in code
- DB passwords, API keys, JWT secrets
- e.g.: `password = "mysql123"`

#### Correct method
See `docs/guides/security-patterns.md` § Secret Management for implementation example.

#### Pre-commit check
See `docs/guides/security-patterns.md` § Secret Management for bash script example.

### Authentication & Authorization

#### Apply authentication to all non-public endpoints

See `docs/guides/security-patterns.md` § Authentication & Authorization for decorator pattern example.

#### Permission check
See `docs/guides/security-patterns.md` § Authentication & Authorization for permission check example.

### Input Validation

#### Validate in Pydantic schema
See `docs/guides/security-patterns.md` § Input Validation for Pydantic validator example.

#### Additional validation in router
See `docs/guides/security-patterns.md` § Input Validation for router-level validation example.

### External Call Safety

#### Timeout setting required
See `docs/guides/security-patterns.md` § External Call Safety for timeout implementation examples.

#### SSL verification
See `docs/guides/security-patterns.md` § External Call Safety for SSL verification examples.

### Pre-Deploy Security Checklist

- [ ] f-string SQL removed (`text()` + binding confirmed)
- [ ] No hardcoded secrets (config.yml verified)
- [ ] All API endpoints have `@RequirePermission()` or explicitly marked public
- [ ] Input validation complete (Pydantic + router)
- [ ] No sensitive information exposed in error responses

---

## Section 2: Error Handling

### Logging Level Criteria

| Level | When to Use | Example |
|-------|------------|---------|
| DEBUG | HTTP request/response | `logger.debug(f"GET /handler/{id}")` |
| INFO | Task completion | `logger.info("Session created: ssi_20250325")` |
| WARNING | Expected failure, partial success | `logger.warning("Handler offline, retrying...")` |
| ERROR | Unexpected failure | `logger.error(f"DB connection failed: {e}")` |

### CRUD ↔ Router Error Boundary

#### CRUD Functions (domain/)
- **Exception propagation**: Propagate SQLAlchemy errors as-is
- **Validation errors**: Raise `ValueError`, `KeyError`
- **Logging**: Use only DEBUG/WARNING when needed

See `docs/guides/security-patterns.md` § Error Handling Patterns for CRUD function example.

#### Router Functions (routers/)
- **Wrap CRUD calls with try-except**
- **Unified response**: `{"result": "OK", "data": ...}` or `{"result": "ERROR", "error": ...}`
- **Logging**: Record at INFO/WARNING/ERROR levels

See `docs/guides/security-patterns.md` § Error Handling Patterns for router function example.

### HTTP Status Codes

| Situation | Code | Example |
|-----------|------|---------|
| Success | 200 | Data returned successfully |
| Invalid input | 400 | Required field missing |
| Unauthenticated | 401 | No token |
| Unauthorized | 403 | Insufficient permissions |
| Resource not found | 404 | Handler ID not found |
| Server error | 500 | Unexpected error |

### Response Format (Consistency)

See `docs/guides/security-patterns.md` § Response Format for JSON structure examples.

**Key rule:** Never use "SUCCESS" — always use "OK"

### Database Error Handling

See `docs/guides/security-patterns.md` § Database Error Handling for SQLAlchemy exception handling example.

---

## Section 3: Git Workflow

### Branch Strategy (Git Flow Variant)

```
master              ← Deployable state (with tags)
  ↑
develop            ← Development integration branch
  ↑
feat/alerts-recent ← Feature branch
test/security-fix
bugfix/session-db
```

#### Rules
- **master**: Merge commit required (`-m` flag)
- **develop**: FF-only merge recommended (linear history)
- **feature branches**: `feat/feature-name`, `bugfix/bug-name`, `test/test-name`

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type
- `feat`: Add new feature
- `fix`: Bug fix
- `refactor`: Code cleanup (no functional change)
- `test`: Add or modify tests
- `docs`: Add/modify documentation
- `chore`: Configuration, dependencies, etc.

#### Scope (optional)
- Component/domain name (e.g., `dashboard`, `sessions`, `auth`)
- Can be omitted

#### Subject
- Imperative present tense ("Fix bug" ✓, "Fixed bug" ✗)
- No period
- Korean allowed (recommended)
- 50 characters or fewer

#### Body (optional)
- What was done (What) + Why it was done (Why)
- 72 characters or fewer per line
- Reference related issues: `Closes #123`

#### Footer (optional)
- Breaking change: `BREAKING CHANGE: description`
- Co-authorship: `Co-Authored-By: name <email>`

### Commit Message Examples

```
feat(dashboard): Add recent alerts query API

Added GET /dashboard/alerts/recent endpoint to query alerts from the last 7 days.

Closes #456
```

```
fix(sessions): Fix session DB insertion omission bug

Fixed a bug where changes were not reflected in DB after calling SessionManager.save().
Transaction commit was missing.

- Added session.commit()
- Added corresponding test

Closes #789
```

### Pre-PR Checklist

- [ ] Branch name follows convention (`feat/...`, `fix/...`)
- [ ] Commit message format verified (type + scope + subject)
- [ ] Synced with latest master commit (`git pull origin master`)
- [ ] ruff check passed (`uv run ruff check issuance_be_fastapi/`)
- [ ] pytest passed (`uv run pytest tests/ -v`)
- [ ] New tests included (when adding features)
- [ ] No secrets/sensitive information committed

### No Force Push Policy

- **master**: Absolutely forbidden
- **develop**: Only after team agreement
- **feature**: Allowed only for individual local work

### Merge Strategy

#### Merge into develop (PR)
```bash
git checkout develop
git pull origin develop
git merge feat/feature-name   # FF-only
git push origin develop
```

#### Merge into master (release)
```bash
git checkout master
git pull origin master
git merge --no-ff develop   # Create merge commit
git tag v1.2.3
git push origin master --tags
```

### Tag Rules

- Format: `v{MAJOR}.{MINOR}.{PATCH}` (Semantic Versioning)
- e.g.: `v1.0.0`, `v1.1.2`
- Tags created on master only

---

## Section 4: Scope Constraints

### Modification Scope
- Only modify the files that were requested
- When fixing bugs, change the minimum number of files
- Do not modify surrounding code under the pretext of "improvement"

### Prohibited Additions
- Do not create new files without being asked
- Do not add docstrings, comments, or type hints to unchanged code
- Do not design for future requirements (YAGNI)
- Do not create helper functions, utilities, or abstractions for one-off tasks

### Protected Files (do not modify without prior confirmation)
- `config.yml`, `.env`, `.env.*`
- `requirements.txt`
- `docker-compose*.yml`, `Dockerfile*`
- `.claude/settings*.json`, `CLAUDE.md`

### Delete / Move
- Delete files only after user confirmation
- Do not delete code that appears unused without confirmation
