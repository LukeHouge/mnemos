# Mnemos

Personal RAG system for managing documents (receipts, manuals, PDFs) with intelligent search and chat. Python 3.12 / FastAPI / PostgreSQL backend.

## Quick Reference

```bash
just harness          # Full verification (ALWAYS run before committing)
just test             # Unit tests only
just check            # Lint + format + type check
just format           # Auto-format code
```

## Documentation (System of Record)

All project knowledge lives in `docs/`. Read these before making changes:

- **[docs/architecture.md](docs/architecture.md)** - Layer structure, dependency rules, file organization
- **[docs/testing.md](docs/testing.md)** - Test philosophy, how to write and run tests
- **[docs/style-guide.md](docs/style-guide.md)** - Code style, formatting, type hints, error handling
- **[docs/commands.md](docs/commands.md)** - All available `just` commands
- **[docs/workflows.md](docs/workflows.md)** - Step-by-step workflows for common tasks

## Architecture Rules (Enforced)

Dependencies flow downward only. Violations fail the structural linter.

```
Routes (app/routes/)  -->  Services (app/services/)  -->  External APIs / DB
   |                          |
   v                          v
Models (app/models/)     Models (app/models/)
```

- **Routes**: Thin HTTP handlers. Delegate to services.
- **Services**: Business logic, external calls.
- **Models**: Pydantic schemas only. No imports from routes or services.
- **Middleware**: Request/response processing. No route/service imports.

## Key Constraints

1. No inline imports - all imports at file top
2. Type hints on all function parameters and return values
3. Modern syntax: `list[str]`, `str | None` (not `List`, `Optional`)
4. Mock at service layer in tests, not at route layer
5. One concept per test, descriptive names
6. No secrets in code, no file paths in error responses
7. Log errors with context, return generic messages to clients

## Verification Workflow

Before every commit:
```bash
just format           # Auto-format
just harness          # Full verification (lint + types + tests + structure)
```

## Project Layout

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Pydantic BaseSettings
│   ├── models/              # Pydantic schemas only
│   ├── routes/              # HTTP handlers (thin)
│   ├── services/            # Business logic
│   └── middleware/           # Request/response processing
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── unit/                # Fast, mocked tests (CI)
│   └── integration/         # Real API tests (optional)
├── scripts/
│   └── lint_structure.py    # Structural architecture linter
└── pyproject.toml           # Dependencies + tool config
```

## Tool Configuration

- **Ruff**: Lint + format rules in `backend/pyproject.toml`
- **Pyright**: Type checking in `backend/pyproject.toml`
- **pytest**: Test config in `backend/pytest.ini`
- **Pre-commit**: Hooks in `.pre-commit-config.yaml`
- **CI**: GitHub Actions in `.github/workflows/ci.yml`
