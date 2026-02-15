# CLAUDE.md - Claude Code Agent Instructions

This file provides instructions for Claude Code (claude-code) when working on the Mnemos project.

## Project Overview

Mnemos is a FastAPI-based Python backend ("Second Brain for Receipts / Manuals / PDFs"). The codebase lives in `backend/` and uses `uv` for package management, `Ruff` for linting/formatting, and `Pyright` for type checking.

## Pre-Commit / Pre-PR Quality Gate (MANDATORY)

**Before EVERY commit and before opening ANY pull request, you MUST run:**

```bash
cd backend && uv run --extra dev ruff check app/ && uv run --extra dev ruff format --check app/ && uv run --extra dev pyright app/
```

Or equivalently:

```bash
just check-local  # Without Docker (for CI agents and local dev)
just check        # With Docker dev container
```

**This is non-negotiable.** No PR should ever be opened with type checking, linting, or formatting failures. If any of these checks fail, fix ALL issues before committing or opening a PR.

Specifically:
- **Pyright type checking** must pass with zero errors
- **Ruff linting** must pass with zero errors
- **Ruff format check** must pass (code must be properly formatted)

If you introduce new code that causes type errors, fix the type errors before committing. Do not use `type: ignore` comments unless absolutely necessary and justified with a comment explaining why.

Pre-commit hooks are configured (`.pre-commit-config.yaml`) and will run these checks automatically on `git commit`, but you should also run them manually before pushing or opening a PR to catch issues early.

## Quick Reference

### Key Commands

```bash
just check        # Lint + format check + type check via Docker (run before every commit)
just check-local  # Same as above but without Docker (for CI agents and local dev)
just format       # Auto-format code (run if format check fails)
just test         # Run unit tests
just test-all     # Run all tests (including integration)
just typecheck    # Run only Pyright type checking
just lint         # Run only Ruff linting
```

### Direct Commands (without Docker)

```bash
cd backend
uv run --extra dev ruff check app/              # Lint
uv run --extra dev ruff format --check app/     # Format check
uv run --extra dev ruff format app/             # Auto-format
uv run --extra dev pyright app/                 # Type check
uv run pytest tests/unit/ -v                    # Unit tests
```

## Coding Standards

### Python Style
- **All imports at the top of the file** -- NEVER use inline imports
- **Explicit imports**: `from app.models.ai import ChatRequest` not `from app.models import ChatRequest`
- **Modern type hints**: `str | None` not `Optional[str]`, `list[str]` not `List[str]`
- **Always use type hints** for function parameters and return values

### Code Organization
- `app/models/` -- Pydantic schemas only
- `app/routes/` -- HTTP route handlers only (thin layer)
- `app/services/` -- Business logic and external service clients
- Keep routes thin, move logic to services
- Never define models in route files

### Error Handling
- Log errors, return generic messages -- never expose internal details
- Use proper HTTP status codes: 503 (service unavailable), 502 (bad gateway), 500 (internal)
- Never mention file paths in error responses

### Testing
- One concept per test, descriptive names (`test_chat_returns_error_when_service_unavailable`)
- Arrange-Act-Assert pattern
- Mock external dependencies in unit tests
- Mark integration tests with `@pytest.mark.integration`

### Documentation
- Docstrings on all public functions, classes, and modules
- Comments explain WHY, not WHAT
- No commented-out code

### Git
- Descriptive commit messages
- Small, focused commits
- Never commit secrets
- **Always run `just check-local` (or `just check` with Docker) before committing and before opening a PR**
- CI status checks (lint, type check, tests) are required to pass before PR merge
