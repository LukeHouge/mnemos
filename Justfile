# Mnemos - Second Brain for Receipts / Manuals / PDFs
# Run `just` or `just --list` to see all available commands

# Default: show available commands
default:
    @just --list

# Start development environment (postgres + dev container)
# Backend container is NOT started by default - use 'just run-dev' to run the app
dev:
    #!/usr/bin/env bash
    set -e
    echo "🛑 Stopping any existing containers..."
    docker compose down 2>/dev/null || true
    echo "🔍 Checking for port conflicts..."
    if docker ps | grep -q " db "; then
        echo "⚠️  Found 'db' container using port 5432. Stopping it..."
        docker stop db || true
    fi
    echo "🚀 Starting postgres and dev container..."
    docker compose up -d postgres dev
    echo "✅ Development environment ready"
    echo "💡 Run 'just run-dev' to start the app with hot reload"
    echo "💡 Or 'just shell' to open a shell in the dev container"

# Start backend container (production-like, for testing production behavior)
start-backend:
    docker compose --profile production up -d backend
    @echo "✅ Backend started (production mode, no hot reload)"
    @echo "📚 API docs: http://localhost:8000/docs"

# Stop backend container
stop-backend:
    docker compose stop backend
    @echo "✅ Backend stopped"

# Run backend server in dev container (with hot reload)
run-dev:
    #!/usr/bin/env bash
    set -e
    echo "🚀 Starting dev server with hot reload..."
    echo "📝 Edit files and they'll auto-reload!"
    echo "📚 API docs: http://localhost:8000/docs"
    echo "🛑 Press Ctrl+C to stop"
    docker compose exec dev sh -c "cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# Build Docker images
build:
    docker compose build

# Start services
up:
    docker compose up -d

# Stop services
down:
    docker compose down

# Restart services
restart:
    docker compose restart

# View logs from all services
logs:
    docker compose logs -f

# View logs from specific service (usage: just logs-backend)
logs-backend:
    docker compose logs -f backend

logs-postgres:
    docker compose logs -f postgres

logs-dev:
    docker compose logs -f dev

# Open shell in dev container (for development)
shell:
    docker compose exec dev bash

# Open shell in backend container (production)
shell-backend:
    docker compose exec backend bash

# Open shell in postgres container
shell-postgres:
    docker compose exec postgres psql -U postgres -d mnemos

# Install/update dependencies in dev container (including dev extras)
sync-deps:
    docker compose exec dev sh -c "cd backend && uv sync --extra dev"

# Install pre-commit hooks
install-hooks:
    docker compose exec dev sh -c "cd backend && uv run pre-commit install"

# Run pre-commit hooks on all files
pre-commit:
    docker compose exec dev sh -c "cd backend && uv run pre-commit run --all-files"

# Add a new dependency (usage: just add-dep sqlalchemy)
add-dep package:
    docker compose exec dev sh -c "cd backend && uv add {{package}}"
    @echo "✅ Added {{package}}. Run 'just sync-deps' if needed."

# Add a dev dependency (usage: just add-dev pytest)
add-dev package:
    docker compose exec dev sh -c "cd backend && uv add --dev {{package}}"
    @echo "✅ Added {{package}} as dev dependency."

# Run unit tests (fast, no external services)
test:
    docker compose exec dev sh -c "cd backend && uv run pytest tests/unit/ -v"

# Run all tests including integration tests (requires OPENAI_API_KEY)
test-all:
    docker compose exec dev sh -c "cd backend && uv run pytest"

# Run tests with coverage report
test-cov:
    docker compose exec dev sh -c "cd backend && uv run pytest tests/unit/ --cov=app --cov-report=html --cov-report=term"
    @echo "📊 Coverage report generated at backend/htmlcov/index.html"

# Run only integration tests (requires API keys)
test-integration:
    docker compose exec dev sh -c "cd backend && uv run pytest tests/integration/ -v"

# Run specific test file
test-file file:
    docker compose exec dev sh -c "cd backend && uv run pytest {{file}} -v"

# Run tests matching a pattern
test-match pattern:
    docker compose exec dev sh -c "cd backend && uv run pytest -k '{{pattern}}' -v"

# Find all TODOs, FIXMEs, and XXX comments in the codebase
todos:
    #!/usr/bin/env bash
    echo "📋 Searching for TODOs, FIXMEs, XXX, HACK, and NOTE comments..."
    echo ""
    echo "Legend:"
    echo "  TODO:  Something to do later"
    echo "  FIXME: Something broken that needs fixing"
    echo "  XXX:   Dangerous/problematic code"
    echo "  HACK:  Temporary workaround"
    echo "  NOTE:  Important information"
    echo ""
    docker compose exec dev sh -c "cd /workspace && grep -rn --include='*.py' --include='*.md' --include='*.yml' --include='*.yaml' --include='*.toml' --include='*.json' -E '(TODO|FIXME|XXX|HACK|NOTE):' . 2>/dev/null | grep -v '.venv' | grep -v '__pycache__' | grep -v '.git' | grep -v 'node_modules' | grep -v '.pytest_cache' | grep -v '.ruff_cache' | grep -v '.mypy_cache' | grep -v 'uv.lock' | grep -v 'package-lock.json' | grep -v 'yarn.lock' | grep -v '^\./\.vscode' | grep -v '^\./\.github/workflows' | sort" || echo "No TODOs found"

# Count TODOs by type
todo-stats:
    #!/usr/bin/env bash
    echo "📊 TODO Statistics:"
    echo ""
    docker compose exec dev sh -c "cd /workspace && echo 'TODO:' && grep -r --include='*.py' --include='*.md' --include='*.yml' --include='*.yaml' --include='*.toml' --include='*.json' 'TODO:' . 2>/dev/null | grep -v '.venv' | grep -v '__pycache__' | grep -v '.pytest_cache' | grep -v '.ruff_cache' | grep -v '.mypy_cache' | grep -v 'uv.lock' | grep -v 'package-lock.json' | grep -v 'yarn.lock' | grep -v '^\./\.vscode' | grep -v '^\./\.github/workflows' | wc -l && echo 'FIXME:' && grep -r --include='*.py' --include='*.md' --include='*.yml' --include='*.yaml' --include='*.toml' --include='*.json' 'FIXME:' . 2>/dev/null | grep -v '.venv' | grep -v '__pycache__' | grep -v '.pytest_cache' | grep -v '.ruff_cache' | grep -v '.mypy_cache' | grep -v 'uv.lock' | grep -v 'package-lock.json' | grep -v 'yarn.lock' | grep -v '^\./\.vscode' | grep -v '^\./\.github/workflows' | wc -l && echo 'XXX:' && grep -r --include='*.py' --include='*.md' --include='*.yml' --include='*.yaml' --include='*.toml' --include='*.json' 'XXX:' . 2>/dev/null | grep -v '.venv' | grep -v '__pycache__' | grep -v '.pytest_cache' | grep -v '.ruff_cache' | grep -v '.mypy_cache' | grep -v 'uv.lock' | grep -v 'package-lock.json' | grep -v 'yarn.lock' | grep -v '^\./\.vscode' | grep -v '^\./\.github/workflows' | wc -l"

# Clean up: remove containers and volumes
clean:
    docker compose down -v
    @echo "⚠️  Removed containers and volumes"

# Clean everything including images
clean-all:
    docker compose down -v --rmi all
    @echo "⚠️  Removed containers, volumes, and images"

# Run database migrations
migrate:
    docker compose exec dev sh -c "cd backend && alembic upgrade head"

# Create new migration (usage: just migrate-create "add users table")
migrate-create message:
    docker compose exec dev sh -c "cd backend && alembic revision --autogenerate -m '{{message}}'"

# Show database status
db-status:
    docker compose exec postgres psql -U postgres -d mnemos -c "\dt"

# Run structural architecture linter (enforces layer boundaries)
lint-structure:
    #!/usr/bin/env bash
    set -e
    cd backend
    python scripts/lint_structure.py

# Full harness verification: lint + typecheck + structural lint + tests
# This is the single command AI agents and humans should run before committing.
harness:
    #!/usr/bin/env bash
    set -e
    echo "=== Harness verification ==="
    cd backend

    echo ""
    echo "--- Ruff lint ---"
    uv run --extra dev ruff check app/

    echo ""
    echo "--- Ruff format check ---"
    uv run --extra dev ruff format --check app/

    echo ""
    echo "--- Pyright type check ---"
    uv run --extra dev pyright app/

    echo ""
    echo "--- Structural architecture lint ---"
    python scripts/lint_structure.py

    echo ""
    echo "--- Unit tests ---"
    uv run pytest tests/unit/ -v

    echo ""
    echo "=== Harness: ALL PASSED ==="

# Check code quality (lint + format check + type check) -- via Docker
check:
    docker compose exec dev sh -c "cd backend && uv run --extra dev ruff check app/ && uv run --extra dev ruff format --check app/ && uv run --extra dev pyright app/"

# Check code quality locally (no Docker -- for Cloud Agents and CI)
check-local:
    #!/usr/bin/env bash
    set -e
    cd backend
    echo "Running Ruff linter..."
    uv run --extra dev ruff check app/
    echo "Running Ruff format check..."
    uv run --extra dev ruff format --check app/
    echo "Running Pyright type checker..."
    uv run --extra dev pyright app/
    echo "All checks passed!"

# Format code (formatting + import sorting) -- via Docker
format:
    docker compose exec dev sh -c "cd backend && uv run --extra dev ruff format app/ && uv run --extra dev ruff check --fix app/"

# Format code locally (no Docker -- for Cloud Agents and CI)
format-local:
    #!/usr/bin/env bash
    set -e
    cd backend
    uv run --extra dev ruff format app/
    uv run --extra dev ruff check --fix app/

# Lint code (check only, no fixes)
lint:
    docker compose exec dev sh -c "cd backend && uv run --extra dev ruff check app/"

# Fix linting issues automatically
lint-fix:
    docker compose exec dev sh -c "cd backend && uv run --extra dev ruff check --fix app/"

# Sort imports
imports:
    docker compose exec dev sh -c "cd backend && uv run --extra dev ruff check --select I --fix app/"

# Type check
typecheck:
    docker compose exec dev sh -c "cd backend && uv run --extra dev pyright app/"

# Run unit tests locally (no Docker -- for Cloud Agents and CI)
test-local:
    #!/usr/bin/env bash
    set -e
    cd backend
    echo "Running unit tests..."
    uv run pytest tests/unit/ -v
    echo "All tests passed!"

# Rebuild and restart backend (useful after Dockerfile changes)
rebuild:
    docker compose build --no-cache backend
    docker compose up -d backend

# Rebuild and restart dev container
rebuild-dev:
    docker compose build --no-cache dev
    docker compose up -d dev

# Show service status
status:
    docker compose ps

# Show resource usage
stats:
    docker stats

# Check if ports are in use
check-ports:
    #!/usr/bin/env bash
    echo "Checking ports..."
    if lsof -i :8000 >/dev/null 2>&1; then
        echo "⚠️  Port 8000 is in use:"
        lsof -i :8000
    else
        echo "✅ Port 8000 is free"
    fi
    if lsof -i :5432 >/dev/null 2>&1; then
        echo "⚠️  Port 5432 is in use:"
        lsof -i :5432
    else
        echo "✅ Port 5432 is free"
    fi
