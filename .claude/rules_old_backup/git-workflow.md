# Git Workflow

## Branch Strategy (Git Flow Variant)

```
master              ← Deployable state (with tags)
  ↑
develop            ← Development integration branch
  ↑
feat/alerts-recent ← Feature branch
test/security-fix
bugfix/session-db
```

### Rules
- **master**: Merge commit required (`-m` flag)
- **develop**: FF-only merge recommended (linear history)
- **feature branches**: `feat/feature-name`, `bugfix/bug-name`, `test/test-name`

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type
- `feat`: Add new feature
- `fix`: Bug fix
- `refactor`: Code cleanup (no functional change)
- `test`: Add or modify tests
- `docs`: Add/modify documentation
- `chore`: Configuration, dependencies, etc.

### Scope (optional)
- Component/domain name (e.g., `dashboard`, `sessions`, `auth`)
- Can be omitted

### Subject
- Imperative present tense ("Fix bug" ✓, "Fixed bug" ✗)
- No period
- Korean allowed (recommended)
- 50 characters or fewer

### Body (optional)
- What was done (What) + Why it was done (Why)
- 72 characters or fewer per line
- Reference related issues: `Closes #123`

### Footer (optional)
- Breaking change: `BREAKING CHANGE: description`
- Co-authorship: `Co-Authored-By: name <email>`

## Commit Message Examples

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

## Pre-PR Checklist

- [ ] Branch name follows convention (`feat/...`, `fix/...`)
- [ ] Commit message format verified (type + scope + subject)
- [ ] Synced with latest master commit (`git pull origin master`)
- [ ] ruff check passed (`uv run ruff check issuance_be_fastapi/`)
- [ ] pytest passed (`uv run pytest tests/ -v`)
- [ ] New tests included (when adding features)
- [ ] No secrets/sensitive information committed

## No Force Push Policy

- **master**: Absolutely forbidden
- **develop**: Only after team agreement
- **feature**: Allowed only for individual local work

## Merge Strategy

### Merge into develop (PR)
```bash
git checkout develop
git pull origin develop
git merge feat/feature-name   # FF-only
git push origin develop
```

### Merge into master (release)
```bash
git checkout master
git pull origin master
git merge --no-ff develop   # Create merge commit
git tag v1.2.3
git push origin master --tags
```

## Tag Rules

- Format: `v{MAJOR}.{MINOR}.{PATCH}` (Semantic Versioning)
- e.g.: `v1.0.0`, `v1.1.2`
- Tags created on master only
