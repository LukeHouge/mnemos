# Development Workflows

## Before Making Any Change

1. Ensure the dev environment is running: `just dev`
2. Verify current state is clean: `just harness`

## Standard Change Workflow

```
1. just test              # Confirm tests pass before starting
2. (make changes)         # Edit code
3. just format            # Auto-format
4. just test              # Run tests
5. just check             # Lint + type check
6. just harness           # Full verification
7. git add + commit       # Commit with descriptive message
```

## Adding a New Route

1. Create/update Pydantic models in `app/models/<domain>.py`
2. Create/update service in `app/services/<service>.py`
3. Create/update route handler in `app/routes/<domain>.py`
4. Register router in `app/main.py` if new file
5. Write unit tests in `tests/unit/test_<domain>_routes.py`
6. Run `just harness`

## Adding a New Model

1. Create model file in `app/models/<domain>.py`
2. Add validation tests in `tests/unit/test_<domain>_models.py`
3. Run `just harness`

## Adding a New Service

1. Create service in `app/services/<name>_service.py`
2. Add singleton pattern if needed (module-level instance)
3. Add fixture in `tests/conftest.py` to clear singleton between tests
4. Write unit tests with mocked external calls in `tests/unit/test_<name>_service.py`
5. Optionally add integration tests in `tests/integration/`
6. Run `just harness`

## Adding a Dependency

```bash
just add-dep <package>     # Production dependency
just add-dev <package>     # Dev-only dependency
just sync-deps             # Sync lock file
```

## Database Changes

1. Modify SQLAlchemy models
2. Create migration: `just migrate-create "description"`
3. Apply migration: `just migrate`
4. Verify: `just db-status`

## Debugging a Test Failure

1. Run the specific failing test: `just test-file tests/unit/test_foo.py`
2. Check if it's a mock issue (wrong patch path)
3. Check if it's a fixture issue (missing singleton clear)
4. Check if structural rules changed: `just lint-structure`
