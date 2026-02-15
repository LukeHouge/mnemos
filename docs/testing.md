# Testing

## Philosophy

Every change must be verifiable by running `just test`. Tests are the primary feedback loop for both human and AI-driven development. If a test can catch a bug, write the test.

## Test Organization

```
backend/tests/
├── conftest.py              # Shared fixtures (client, service resets)
├── unit/                    # Fast, fully mocked - runs in CI
│   ├── test_*_routes.py     # Route tests (mocked services)
│   ├── test_*_service.py    # Service tests (mocked clients)
│   └── test_*_models.py     # Model validation tests
└── integration/             # Real API calls - requires credentials
    └── test_*_service.py    # Real external service tests
```

## Running Tests

```bash
# Unit tests only (default, fast, no credentials needed)
just test

# All tests including integration
just test-all

# Integration tests only (requires OPENAI_API_KEY)
just test-integration

# Coverage report
just test-cov

# Specific file
just test-file tests/unit/test_health_routes.py

# Pattern match
just test-match "test_chat"
```

## Writing Tests

### Unit Tests
- Mock all external dependencies (`@patch` decorator with full import paths)
- Mock at the service layer, not at the route layer
- One concept per test function
- Descriptive names: `test_chat_returns_error_when_service_unavailable`
- Use Arrange-Act-Assert pattern
- All imports at top of file (no inline imports)

### Integration Tests
- Mark with `@pytest.mark.integration`
- Skip when credentials missing: `@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"))`
- Test real API behavior, error handling, and edge cases

### Fixtures
- Shared fixtures live in `conftest.py`
- Service singleton clearing fixture ensures test isolation
- FastAPI `TestClient` fixture for route testing

## CI Behavior

The CI pipeline (`ci.yml`) runs:
1. Ruff lint + format check
2. Pyright type check
3. Unit tests with PostgreSQL service
4. Coverage report (uploaded as artifact)

Integration tests are NOT run in CI (they require API keys).

## Test-Driven Feedback Loop

When working on a change:
1. Run `just test` to verify current state passes
2. Write or modify tests for the change
3. Implement the change
4. Run `just test` to verify
5. Run `just check` to verify linting/types
6. Run `just harness` for full verification
