# Commands Reference

All commands are defined in the `Justfile` and run via `just <command>`. Run `just` to see the full list.

## Verification (Harness)

```bash
just harness          # Full verification: lint + typecheck + test + structural lint
just check            # Lint + format check + type check
just test             # Unit tests only (fast)
just lint-structure   # Structural architecture linter
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
just test             # Unit tests (fast, no credentials)
just test-all         # All tests including integration
just test-integration # Integration tests only
just test-cov         # Unit tests with coverage report
just test-file <f>    # Run specific test file
just test-match <p>   # Run tests matching pattern
```

## Code Quality

```bash
just check            # Lint + format check + type check
just format           # Auto-format code
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
