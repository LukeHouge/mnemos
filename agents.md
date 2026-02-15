# Mnemos - Agent Context

Quick-reference for AI agents (Cursor, Copilot, etc.) working in this repository.

## What Is Mnemos?

**Second Brain for Receipts / Manuals / PDFs** - A personal RAG (Retrieval-Augmented Generation) system for managing documents with intelligent search and chat.

**Use case:** Upload PDFs (warranties, invoices, travel docs, medical bills, dog docs, car service receipts), auto-tag them, extract key fields, and chat + search with citations.

## Current State (Early Stage)

The project has a solid backend skeleton and dev tooling, but the core document management features are **not yet built**. Here's what exists today:

### What's Built

| Component | Status | Details |
|-----------|--------|---------|
| FastAPI backend | Working | Python 3.12, running on uvicorn |
| OpenAI integration | Working | Chat completions via `gpt-4o-mini`, async client, singleton service |
| Health checks | Working | Basic (`/api/v1/health`) and detailed (`/api/v1/health/full`) with service status |
| Middleware stack | Working | Request ID tracing, request/response logging, security headers, CORS |
| Pydantic models | Working | Typed request/response schemas with validation |
| Structured logging | Working | Rich-formatted console logging with context fields |
| PostgreSQL | Configured | Docker container runs, but no tables/models/migrations yet |
| Alembic | Configured | Dependency installed, `just migrate` commands ready, but no migrations |
| Docker Compose | Working | Dev container, production container, PostgreSQL |
| CI/CD | Working | GitHub Actions: Ruff lint, Pyright type check, pytest with coverage |
| Pre-commit hooks | Working | Ruff lint, Ruff format, Pyright, trailing whitespace, etc. |
| Test suite | Working | Unit tests (mocked) + integration tests (real OpenAI) |
| TODO tracking | Working | `just todos`, GitHub Action comments new TODOs on PRs |
| Dev container | Working | VS Code/Cursor devcontainer with extensions, format-on-save |

### What's NOT Built Yet

These are the **core features** described in the README that don't exist in code:

- **PDF upload and storage** - No upload endpoints, no file storage
- **Document parsing / text extraction** - No PDF-to-text pipeline
- **Auto-tagging** - No classification or tagging system
- **Key field extraction** - No structured data extraction from documents
- **Search with citations** - No search endpoints, no vector embeddings
- **RAG pipeline** - No retrieval-augmented generation (the chat endpoint exists but doesn't search documents)
- **Database models** - No SQLAlchemy ORM models, no tables, no migrations
- **Vector database (Qdrant)** - Referenced in TODOs but not integrated
- **Frontend** - Next.js mentioned as "coming soon" in README
- **User authentication** - No auth system

## Architecture

```
mnemos/
├── backend/                    # FastAPI backend (Python 3.12)
│   ├── app/
│   │   ├── main.py            # FastAPI app, middleware, exception handlers
│   │   ├── config.py          # Pydantic BaseSettings (env vars)
│   │   ├── logging_config.py  # Rich logging setup
│   │   ├── models/            # Pydantic request/response schemas
│   │   │   ├── ai.py          # ChatRequest, ChatResponse
│   │   │   ├── health.py      # HealthCheck, DetailedHealthCheck
│   │   │   ├── common.py      # ServiceStatus (shared)
│   │   │   └── errors.py      # ErrorResponse, ErrorDetail
│   │   ├── routes/            # HTTP route handlers (thin layer)
│   │   │   ├── ai.py          # POST /api/v1/ai/chat, GET /api/v1/ai/test
│   │   │   └── health.py      # GET /api/v1/health, GET /api/v1/health/full
│   │   ├── services/          # Business logic and external clients
│   │   │   └── openai_service.py  # OpenAI async client (singleton)
│   │   └── middleware/        # Request processing pipeline
│   │       ├── request_id.py  # X-Request-ID generation/propagation
│   │       ├── logging.py     # Request/response logging with timing
│   │       └── security.py    # Security headers (HSTS, XSS, etc.)
│   ├── tests/
│   │   ├── conftest.py        # Shared fixtures (client, mock_openai_key)
│   │   ├── unit/              # Fast mocked tests (run in CI)
│   │   └── integration/       # Real API tests (require credentials)
│   ├── pyproject.toml         # Dependencies, Ruff config, Pyright config
│   ├── Dockerfile             # Production image
│   └── Dockerfile.dev         # Dev image (with dev tools)
├── .github/workflows/
│   ├── ci.yml                 # Lint + type check + test on push/PR
│   └── todos.yml              # Comment new TODOs on PRs
├── docker-compose.yml         # postgres, backend (prod), dev containers
├── Justfile                   # Command runner (just dev, just test, etc.)
├── .cursorrules               # Coding standards for AI agents
└── .pre-commit-config.yaml    # Pre-commit hooks
```

### Key Patterns

- **Separation of concerns**: Models (Pydantic schemas) / Routes (thin HTTP handlers) / Services (business logic)
- **Dependency injection**: Services injected into routes via `Depends(get_service)`
- **Singleton services**: `get_openai_service()` returns a module-level singleton
- **Async-first**: `AsyncOpenAI` client, async route handlers
- **Environment-driven config**: `Pydantic BaseSettings` reads from env vars set by Docker Compose
- **Secrets separation**: `.env.dev` (safe defaults, committed) + `.env.secrets` (gitignored)

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API root (version, links) |
| GET | `/docs` | **Swagger UI** - Interactive API documentation |
| GET | `/redoc` | **ReDoc** - Alternative API documentation |
| GET | `/api/v1/health` | Basic health (load balancer) |
| GET | `/api/v1/health/full` | Detailed health (all services) |
| POST | `/api/v1/ai/chat` | Chat with AI assistant |
| GET | `/api/v1/ai/test` | Test OpenAI connectivity |

FastAPI auto-generates OpenAPI (Swagger) docs from route definitions, Pydantic models, and docstrings. Visit http://localhost:8000/docs when the server is running to explore and test endpoints interactively.

## Roadmap & Planned Work

Derived from TODOs in code, README mentions, and architectural signals:

### Near-term

1. **Database models & migrations** - SQLAlchemy ORM models for documents, tags, users. Alembic migrations. PostgreSQL is already running.
2. **Database health check** - `TODO` in `backend/app/routes/health.py` line 50
3. **Production env file** - `TODO` in `docker-compose.yml` line 31 to switch `.env.dev` to `.env.prod`

### Medium-term

4. **PDF upload & storage** - Upload endpoint, file storage (local or S3), document model
5. **Document parsing** - PDF text extraction (e.g., PyMuPDF, pdfplumber, or unstructured)
6. **Auto-tagging & field extraction** - Use OpenAI to classify documents and extract structured fields
7. **Vector database (Qdrant)** - `TODO` in `backend/app/routes/health.py` line 51. Store document embeddings for semantic search.
8. **RAG pipeline** - Connect chat endpoint to document retrieval. Embed documents, search by similarity, feed context to LLM.
9. **Search endpoint** - Full-text and/or semantic search with citations back to source documents

### Longer-term

10. **Next.js frontend** - Referenced in README as "coming soon". Devcontainer already forwards port 3000 and includes ESLint/Prettier/Tailwind extensions.
11. **User authentication** - No auth system exists. Route organization hints at future `/users/` routes.
12. **Multi-user support** - Currently single-user design assumptions

## Active TODOs in Code

| Location | TODO |
|----------|------|
| `backend/app/routes/health.py:50` | Add database health check when we have DB connections |
| `backend/app/routes/health.py:51` | Add Qdrant health check when vector DB is added |
| `docker-compose.yml:31` | For production: change `.env.dev` to `.env.prod` |

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Language | Python 3.12 | Modern syntax (`str \| None`, `list[str]`) |
| Framework | FastAPI | Async, Pydantic validation, auto-docs |
| AI | OpenAI API | `gpt-4o-mini` default, async client |
| Database | PostgreSQL 15 | Alpine image, async driver (`asyncpg`) |
| ORM | SQLAlchemy 2.0 | Installed but not yet used |
| Migrations | Alembic | Installed but no migrations created |
| Package manager | uv | Fast Python package manager |
| Linter/Formatter | Ruff | Replaces flake8, black, isort |
| Type checker | Pyright | Basic mode |
| Testing | pytest | pytest-asyncio, pytest-cov, httpx TestClient |
| Logging | Rich | Colored console output, tracebacks |
| Containers | Docker Compose | Dev + prod + postgres |
| CI | GitHub Actions | Lint, type check, test with coverage |
| Command runner | just | `just dev`, `just test`, `just check` |

## Working in This Repo

### Quick Commands

```bash
# With Docker (local dev)
just dev          # Start postgres + dev container
just run-dev      # Run backend with hot reload
just test         # Run unit tests
just check        # Lint + type check
just format       # Auto-format code
just shell        # Shell into dev container
just todos        # Find all TODOs

# Without Docker (Cloud Agents, CI)
just check-local  # Lint + format check + type check
just format-local # Auto-format code
just test-local   # Run unit tests
```

### Cloud Agent Environment

Agent environments are bootstrapped automatically via `scripts/setup-agent-env.sh`:
- **Cursor Cloud Agents**: `.cursor/setup.sh` calls it on VM start
- **Claude Code**: `.claude/settings.json` SessionStart hook calls it on session start

The script installs `uv`, `just`, and all Python dependencies. Use `just harness` (already runs locally) and `-local` command variants (e.g., `just check-local`, `just format-local`, `just test-local`) in agent environments since Docker is not available.

### Adding a New Feature

1. **Models** go in `backend/app/models/<feature>.py` - Pydantic schemas only
2. **Services** go in `backend/app/services/<feature>_service.py` - Business logic, external clients
3. **Routes** go in `backend/app/routes/<feature>.py` - Thin HTTP handlers, use `Depends()` for services
4. **Register router** in `backend/app/main.py` with `app.include_router()`
5. **Tests** go in `backend/tests/unit/test_<feature>_*.py` (mocked) and `backend/tests/integration/` (real)

### Code Style Essentials

- **All imports at top of file** - Never inline imports
- **Explicit imports** - `from app.models.ai import ChatRequest` not `from app.models import ChatRequest`
- **Type hints everywhere** - Parameters and return values
- **Modern syntax** - `str | None` not `Optional[str]`, `list[str]` not `List[str]`
- **Docstrings on everything** - Modules, classes, public functions
- **Log errors, return generic messages** - Never expose internals to users
- **HTTP status codes** - 503 (not configured), 502 (external error), 500 (unexpected)

### Testing Rules

- **Unit tests mock all external deps** - Use `@patch` with full paths
- **One concept per test** - Descriptive names like `test_chat_returns_error_when_service_unavailable`
- **Arrange-Act-Assert** pattern
- **Integration tests** use `@pytest.mark.integration` and `@pytest.mark.skipif` for credentials

### Validating Your Changes

Before committing, run these checks to ensure nothing is broken.

**Minimum validation (must pass before every commit):**

```bash
# With Docker:
just check        # Lint (Ruff) + format check (Ruff) + type check (Pyright)
just test         # Run all unit tests

# Without Docker (Cloud Agents, CI):
just check-local  # Same checks, runs directly on host
just test-local   # Same tests, runs directly on host
```

These commands mirror exactly what CI runs on every push/PR. If they pass locally, CI will pass.

**Step-by-step validation:**

```bash
# 1. Lint - catches style issues, unused imports, common bugs
just lint         # Check only
just lint-fix     # Auto-fix what it can

# 2. Format - ensures consistent code style
just format       # Auto-format code and sort imports

# 3. Type check - catches type errors
just typecheck    # Pyright in basic mode

# 4. Unit tests - fast, no external services needed
just test                          # All unit tests
just test-file tests/unit/test_ai_routes.py  # Specific file
just test-match "chat"             # Tests matching pattern

# 5. Integration tests (optional, requires OPENAI_API_KEY)
just test-integration

# 6. Coverage report
just test-cov     # Generates HTML report at backend/htmlcov/
```

**Without Docker (e.g., in CI or running directly on host):**

```bash
cd backend
uv run ruff check app/              # Lint
uv run ruff format --check app/     # Format check
uv run pyright app/                 # Type check
uv run pytest tests/unit/ -v        # Unit tests
```

**What CI checks on every push/PR (see `.github/workflows/ci.yml`):**
- Ruff linting (`ruff check app/`)
- Ruff format check (`ruff format --check app/`)
- Pyright type checking (`pyright app/`)
- All unit tests with coverage (`pytest tests/unit/ --cov=app`)

**Pre-commit hooks (if installed):**

```bash
just install-hooks   # One-time setup
# Now git commit will auto-run: ruff check, ruff format --check, pyright
```

**Fixing failures:**
- `just format` and `just lint-fix` auto-fix most lint/format issues
- Pyright errors require manual fixes to type annotations
- Test failures: read the assertion output, check the Arrange-Act-Assert structure

### What NOT to Do

- Don't add features speculatively (YAGNI)
- Don't commit secrets or `.env.secrets`
- Don't define models in route files
- Don't use inline imports
- Don't leave commented-out code
- Don't expose file paths or internal details in error responses
