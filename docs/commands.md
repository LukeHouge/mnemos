# Commands Reference

All commands are defined in the `Justfile` and run via `just <command>`. Run `just` to see the full list.

## Verification (Harness)

```bash
just harness          # Full verification: lint + typecheck + test + structural lint (runs locally, no Docker)
just check            # Lint + format check + type check (Docker)
just test             # Unit tests only (Docker)
just lint-structure   # Structural architecture linter (runs locally)
```

## Local Variants (No Docker -- for Cloud Agents and CI)

These run directly on the host without Docker. Environment setup is handled automatically by `scripts/setup-agent-env.sh` (called by `.cursor/environment.json` install command and `.claude/settings.json` SessionStart hook).

```bash
just harness          # Already runs locally -- no -local variant needed
just check-local      # Lint + format check + type check
just format-local     # Auto-format code
just test-local       # Unit tests
```

## Development

```bash
just dev              # Start postgres + dev container
just run-dev          # Run app with hot reload
just shell            # Open dev container shell
just sync-deps        # Install/update dependencies
```

## Testing

```bash
just test             # Unit tests via Docker (fast, no credentials)
just test-local       # Unit tests directly on host
just test-all         # All tests including integration
just test-integration # Integration tests only
just test-cov         # Unit tests with coverage report
just test-file <f>    # Run specific test file
just test-match <p>   # Run tests matching pattern
```

## Code Quality

```bash
just check            # Lint + format check + type check (Docker)
just check-local      # Same, no Docker
just format           # Auto-format code (Docker)
just format-local     # Same, no Docker
just lint             # Lint check only
just lint-fix         # Auto-fix linting issues
just typecheck        # Pyright type checking
just imports          # Sort imports
just lint-structure   # Structural architecture validation
```

## Database

```bash
just migrate                  # Run migrations
just migrate-create "msg"     # Create new migration
just db-status                # Show tables
```

## Docker

```bash
just build            # Build images
just up / down        # Start / stop services
just restart          # Restart services
just logs             # View all logs
just status           # Show service status
```

## Agent Environment Setup

```bash
bash scripts/setup-agent-env.sh   # Install uv, just, and all Python deps
```

This is called automatically by `.cursor/environment.json` (Cursor Cloud Agents) and `.claude/settings.json` (Claude Code). Run manually if needed.
