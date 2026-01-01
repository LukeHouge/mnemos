# Mnemos - Second Brain for Receipts / Manuals / PDFs
# Run `just` or `just --list` to see all available commands

# Default: show available commands
default:
    @just --list

# Start development environment (all services including dev container)
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
    echo "🚀 Starting services..."
    docker compose up -d
    echo "✅ Services started"
    echo "📚 API docs: http://localhost:8000/docs"
    echo "🔍 Health check: http://localhost:8000/health"
    echo "💡 Use 'just shell' to open a shell in the dev container"

# Run backend server in dev container (with hot reload)
run-dev:
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

# Add a new dependency (usage: just add-dep sqlalchemy)
add-dep package:
    docker compose exec dev sh -c "cd backend && uv add {{package}}"
    @echo "✅ Added {{package}}. Run 'just sync-deps' if needed."

# Add a dev dependency (usage: just add-dev pytest)
add-dev package:
    docker compose exec dev sh -c "cd backend && uv add --dev {{package}}"
    @echo "✅ Added {{package}} as dev dependency."

# Run tests
test:
    docker compose exec dev sh -c "cd backend && uv run pytest"

# Run tests with coverage
test-cov:
    docker compose exec dev sh -c "cd backend && uv run pytest --cov=app --cov-report=html"

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

# Check code quality (lint + type check)
check:
    docker compose exec dev sh -c "cd backend && uv run ruff check app/ && uv run pyright app/"

# Format code (formatting + import sorting)
format:
    docker compose exec dev sh -c "cd backend && uv run ruff format app/ && uv run ruff check --fix app/"

# Lint code (check only, no fixes)
lint:
    docker compose exec dev sh -c "cd backend && uv run ruff check app/"

# Fix linting issues automatically
lint-fix:
    docker compose exec dev sh -c "cd backend && uv run ruff check --fix app/"

# Sort imports
imports:
    docker compose exec dev sh -c "cd backend && uv run ruff check --select I --fix app/"

# Type check
typecheck:
    docker compose exec dev sh -c "cd backend && uv run pyright app/"

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

