# Mnemos

**Second Brain for Receipts / Manuals / PDFs** - A personal RAG system for managing documents with intelligent search and chat.

## What It Is

Upload PDFs (warranties, invoices, travel docs, medical bills, dog docs, car service receipts), auto-tag them, extract key fields, and chat + search with citations.

## Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **Frontend**: Next.js (coming soon)
- **Database**: PostgreSQL

## Prerequisites

- Docker Desktop ([install](https://www.docker.com/products/docker-desktop))
- `just` command runner ([install](https://github.com/casey/just))

## Quick Start

1. **Create secrets file:**
   ```bash
   cp backend/.env.secrets.example backend/.env.secrets
   # Edit backend/.env.secrets and set your SECRET_KEY
   ```

2. **Start services:**
   ```bash
   just dev
   ```
   This will:
   - Build the Docker images (first time only)
   - Start postgres, backend, and dev containers
   - Install dependencies in the dev container

3. **If using Cursor/VS Code:**
   - Open the project in Cursor/VS Code
   - When prompted, click "Reopen in Container" (or use Command Palette → "Dev Containers: Reopen in Container")
   - This attaches your editor to the `dev` container

4. **Access the API:**
   - API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

5. **Install pre-commit hooks (recommended):**
   ```bash
   just install-hooks
   ```
   This will automatically run linting and type checking before each commit.

## Development

### Available Commands

Run `just` or `just --list` to see all commands. Common ones:

- `just dev` - Start development environment (postgres, backend, and dev containers)
- `just sync-deps` - Install dependencies after adding new ones (in dev container)
- `just shell` - Open shell in dev container
- `just run-dev` - Run backend server with hot reload in dev container
- `just logs-backend` - View backend logs (production container)
- `just logs-dev` - View dev container logs
- `just test` - Run tests (in dev container)
- `just check` - Run all code quality checks (lint + type check)
- `just format` - Format code and fix auto-fixable issues
- `just lint` - Check code for linting issues
- `just lint-fix` - Fix linting issues automatically
- `just typecheck` - Run type checking with Pyright
- `just install-hooks` - Install pre-commit hooks
- `just pre-commit` - Run pre-commit hooks manually on all files

### Adding Dependencies

```bash
# Add a production dependency
just add-dep sqlalchemy

# Add a dev dependency
just add-dev pytest

# Then sync in container (if needed)
just sync-deps
```

### Project Structure

```
mnemos/
├── backend/          # FastAPI backend
│   ├── app/         # Application code
│   ├── Dockerfile   # Production image
│   ├── Dockerfile.dev  # Development image (with dev tools)
│   └── pyproject.toml
├── .devcontainer/    # VS Code/Cursor dev container config
│   └── devcontainer.json
├── frontend/         # Next.js frontend (coming soon)
├── docker-compose.yml
└── Justfile          # Command shortcuts
```

### Container Architecture

The project uses **separate containers** for development and production:

- **`dev` container**: Your development environment with dev tools, mounted volumes for live editing
- **`backend` container**: Production-ready FastAPI server (no dev tools, optimized for production)
- **`postgres` container**: PostgreSQL database

When using Cursor/VS Code with the devcontainer, you'll be working in the `dev` container. The `backend` container runs the production server separately.

### Code Quality Tools

The project uses **Ruff** for linting, formatting, and import sorting, and **Pyright** for type checking.

**Quick commands:**
- `just check` - Run all checks (lint + type check)
- `just format` - Format code and organize imports
- `just lint` - Check for linting issues
- `just lint-fix` - Auto-fix linting issues
- `just imports` - Sort imports only
- `just typecheck` - Run type checking

**How the commands work:**
- `docker compose exec dev` - Runs the command in the running `dev` container
- `sh -c` - Executes the command string in a shell (needed for complex commands)
- `uv run` - Runs the tool in uv's managed virtual environment (ensures correct Python and dependencies)

**Why `uv run` instead of running tools directly?**
- Guarantees the correct Python version and environment
- Ensures all dependencies are available
- Works consistently across different systems

**Inside the dev container:**
```bash
cd backend
uv run ruff check app/        # Lint
uv run ruff format app/        # Format
uv run pyright app/            # Type check
```

### Pre-commit Hooks

Pre-commit hooks automatically check your code before each commit:

**Setup (one-time):**
```bash
just install-hooks
```

**What gets checked:**
- Ruff linting and formatting (auto-fixes issues)
- Pyright type checking (using project environment)
- Trailing whitespace (auto-fixes)
- End of file newlines (auto-fixes)
- YAML/JSON/TOML syntax
- Large file prevention

**Manual run:**
```bash
just pre-commit  # Run on all files
```

**Skip hooks (when needed):**
```bash
git commit --no-verify
```

**IDE Integration:**
- Ruff and Pyright are configured to run automatically in VS Code/Cursor
- Format on save is enabled
- Import organization happens automatically on save
- Install the "Ruff" extension (already in devcontainer.json)

**Configuration:**
- Ruff settings: `backend/pyproject.toml` (under `[tool.ruff]`)
- Pyright settings: `backend/pyproject.toml` (under `[tool.pyright]`)
- VS Code settings: `.vscode/settings.json`

### Environment Variables

The project uses a clean environment file strategy:
- `backend/.env.dev` - Development defaults (checked into git, no secrets)
- `backend/.env.secrets` - **Only secrets** (gitignored, **required**)
- Later: `backend/.env.prod` - Production config (no secrets)

**Setup:**
1. Copy the example secrets file:
   ```bash
   cp backend/.env.secrets.example backend/.env.secrets
   ```

2. Edit `backend/.env.secrets` and set your `SECRET_KEY`:
   ```bash
   # Generate a random secret key
   python -c "import secrets; print(f'SECRET_KEY={secrets.token_urlsafe(32)}')"
   # Copy the output to backend/.env.secrets
   ```

**How it works:**
- Docker Compose loads `.env.dev` and `.env.secrets` files
- Environment variables are passed to containers
- `.env.secrets` values override `.env.dev` values
- `config.py` reads from environment variables (agnostic to file source)
- Production can use different files: just change `env_file` in docker-compose.yml
- Never commit `.env.secrets` to git
