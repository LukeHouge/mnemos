# Mnemos

Personal RAG system for managing documents (receipts, manuals, PDFs) with intelligent search and chat. Python 3.12 / FastAPI / PostgreSQL backend.

## Environment Setup (Automated)

Agent environments are bootstrapped automatically:
- **Cursor Cloud Agents**: `.cursor/setup.sh` runs on VM start
- **Claude Code**: `.claude/settings.json` SessionStart hook runs on session start

Both call the shared `scripts/setup-agent-env.sh` which installs `uv`, `just`, and all Python dependencies. Manual re-run: `bash scripts/setup-agent-env.sh`

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
- `docs/ci-and-agents.md` - CI health checks, agent permissions, branch protection

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

## Agent Boundaries (STRICT)

Agents must NEVER perform these actions, even if technically possible:

1. **NEVER merge a PR** — merging is always a human decision (`gh pr merge` is forbidden)
2. **NEVER mark a PR as ready for review** — the author decides when it's ready (`gh pr ready` is forbidden)
3. **NEVER approve or review a PR** — reviews are human-only
4. **NEVER close or reopen issues or PRs** — lifecycle decisions belong to humans
5. **NEVER push directly to `main`** — always work on feature branches

Agents SHOULD: push code to feature branches, read CI results, iterate on fixes until checks pass, and report findings. Humans decide when to approve, merge, and release.

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
