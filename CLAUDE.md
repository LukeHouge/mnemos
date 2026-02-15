# Claude Code Instructions

## Mandatory Pre-Commit Validation

**CRITICAL: You MUST run these checks before every commit and before opening any PR. No exceptions.**

```bash
just check        # Lint (Ruff) + format check (Ruff) + type check (Pyright)
just test         # Run all unit tests
```

If either command fails, fix ALL errors before committing. Do NOT commit or open a PR with failing type checks, lint errors, or test failures.

**If running outside Docker / without `just`:**

```bash
cd backend
uv run ruff check app/              # Lint
uv run ruff format --check app/     # Format check
uv run pyright app/                 # Type check
uv run pytest tests/unit/ -v        # Unit tests
```

## Pre-PR Checklist

Before opening any pull request, verify:

1. `just check` passes (zero lint errors, zero format errors, zero type errors)
2. `just test` passes (all unit tests green)
3. No secrets or `.env.secrets` files are staged
4. Commit messages are descriptive

## Quick Reference

- **Format code:** `just format` (auto-fixes formatting and import sorting)
- **Fix lint issues:** `just lint-fix` (auto-fixes what it can)
- **Type errors:** Must be fixed manually — update type annotations, add missing types, fix incompatible types
- **Run specific tests:** `just test-file tests/unit/test_ai_routes.py`

## Project Conventions

See `.cursorrules` for full coding standards. Key points:

- All imports at top of file (never inline)
- Type hints on all function parameters and return values
- Modern Python syntax: `str | None` not `Optional[str]`, `list[str]` not `List[str]`
- Models in `app/models/`, routes in `app/routes/`, logic in `app/services/`
- Keep routes thin — business logic goes in services
- Log errors, return generic messages to users
