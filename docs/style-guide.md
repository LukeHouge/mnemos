# Style Guide

All style rules are enforced mechanically via Ruff and Pyright (configured in `backend/pyproject.toml`). Structural rules are enforced by `backend/scripts/lint_structure.py`.

## Python

### Imports
- All imports at top of file. Never inline imports.
- Explicit imports: `from app.models.ai import ChatRequest` not `from app.models import ChatRequest`
- Import order: stdlib, third-party, local (enforced by Ruff isort)
- Avoid `__all__` unless absolutely necessary

### Type Hints
- Always type function parameters and return values
- Modern syntax: `list[str]`, `dict[str, int]`, `str | None`
- Never use `List`, `Dict`, `Optional` from typing

### Error Handling
- Log errors, return generic messages to clients
- HTTP status codes: 503 (service unavailable), 502 (external API error), 500 (unexpected)
- Never expose file paths or internal details in error responses

### Logging
- Structured logging with `logger.info/error`
- Context via `extra={}` for important fields
- Levels: DEBUG (diagnostic), INFO (general), WARNING (warnings), ERROR (with exceptions)

### Configuration
- Pydantic BaseSettings for all config
- Environment variables via Docker Compose
- Sensible defaults for dev/test, required values for production
- No secrets in code

## Formatting

Enforced by Ruff formatter:
- Double quotes for strings
- 100 character line limit
- Space indentation
- Magic trailing commas preserved

## Comments

- Explain WHY, not WHAT
- TODO format: `TODO(#123): Description` or `TODO: Description`
- Comment types: `TODO:`, `FIXME:`, `XXX:`, `HACK:`, `NOTE:`
- No commented-out code (use git history)

## YAGNI

- Don't add features speculatively
- Remove unused code
- Simplify when possible
