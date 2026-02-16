# Mnemos

Personal RAG system for managing documents (receipts, manuals, PDFs) with intelligent search and chat. Python 3.12 / FastAPI / PostgreSQL backend.

## Environment Setup (Automated)

Agent environments are bootstrapped automatically:
- **Cursor Cloud Agents**: `.cursor/environment.json` `install` command runs `scripts/setup-agent-env.sh` on VM setup (result is snapshotted for fast subsequent starts)
- **Claude Code**: `.claude/settings.json` SessionStart hook runs `scripts/setup-agent-env.sh` on session start

The script installs `uv`, `just`, and all Python dependencies. Manual re-run: `bash scripts/setup-agent-env.sh`

## Quick Reference

```bash
just harness          # Full verification (ALWAYS run before committing, runs locally)
just format-local     # Auto-format code (no Docker)
just check-local      # Lint + format + type check (no Docker)
just test-local       # Unit tests (no Docker)
```

In agent/CI environments without Docker, use the `-local` variants for `format`, `check`, and `test`. `just harness` already runs locally (no Docker needed).

## Documentation (System of Record)

All project knowledge lives in `docs/`. Read these before making changes:

- `docs/architecture.md` - Layer structure, dependency rules, file organization
- `docs/testing.md` - Test philosophy, how to write and run tests
- `docs/style-guide.md` - Code style, formatting, type hints, error handling
- `docs/commands.md` - All available `just` commands
- `docs/workflows.md` - Step-by-step workflows for common tasks

## Architecture Rules (Enforced)

Dependencies flow downward only. Violations fail `just lint-structure`.

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

## Verification Workflow

Before every commit:
```bash
just format           # Auto-format
just harness          # Full verification (lint + types + tests + structure)
```

## Project Layout

```
backend/
├── app/                     # Application code
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Pydantic BaseSettings
│   ├── models/              # Pydantic schemas only
│   ├── routes/              # HTTP handlers (thin)
│   ├── services/            # Business logic
│   └── middleware/           # Request/response processing
├── tests/
│   ├── unit/                # Fast, mocked tests (CI)
│   └── integration/         # Real API tests (optional)
├── scripts/
│   └── lint_structure.py    # Structural architecture linter
└── pyproject.toml           # Dependencies + tool config
docs/                        # Project knowledge base (system of record)
```
