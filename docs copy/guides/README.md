# Security & Development Guides

This directory contains practical guides and code examples referenced by the `.claude/rules/` documentation.

## Available Guides

### security-patterns.md
**Purpose:** Code examples for security and error handling patterns

**Contents:**
- SQL Injection Prevention (safe & forbidden patterns)
- Secret Management (configuration loading, pre-commit checks)
- Authentication & Authorization (decorators, permission checks)
- Input Validation (Pydantic schemas, router validation)
- External Call Safety (timeouts, SSL verification)
- Error Handling (CRUD/Router patterns, database exceptions)
- Response Format (JSON structure standards)

**Cross-referenced by:** `.claude/rules/critical-rules.md`

**When to Use:**
- You see a rule in `critical-rules.md` that references this file
- You're implementing security features (SQL queries, authentication, validation)
- You need concrete code examples for error handling patterns

---

## Document Structure

Each guide is organized with:
1. **Overview:** What the guide covers
2. **Code sections:** Practical examples with comments
3. **Cross-references:** Links back to related rules

---

## Related Documentation

- `.claude/rules/critical-rules.md` — Security rules, error handling standards, git workflow
- `.claude/rules/` — Complete rules directory
- `/docs/` — Root documentation directory

---

**Last Updated:** 2026-04-17
