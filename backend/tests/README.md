# Tests

Organized test structure for the Mnemos backend.

## Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Fast tests, no external dependencies
│   ├── test_*_routes.py    # Route/endpoint tests (mocked services)
│   ├── test_*_service.py   # Service layer tests (mocked clients)
│   └── test_*_models.py    # Model/schema tests
├── integration/             # Tests with real external services
│   ├── test_*_service.py   # Real API calls (requires credentials)
│   └── test_*_e2e.py       # End-to-end tests
└── README.md               # This file
```

## Running Tests

```bash
# All unit tests (fast, no external calls)
just test

# Specific test file
just shell
cd backend
uv run pytest tests/unit/test_ai_routes.py -v

# Specific test function
uv run pytest tests/unit/test_ai_routes.py::test_chat_success -v

# Integration tests (requires OPENAI_API_KEY)
just test-integration

# All tests
just test-all

# With coverage
just test-cov
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **Fast** - Run in milliseconds
- **Isolated** - Mock all external dependencies
- **Reliable** - No network calls, no external state
- **CI-friendly** - Run on every commit

**Naming convention:** `test_{feature}_{layer}.py`
- `test_ai_routes.py` - AI endpoint tests
- `test_openai_service.py` - OpenAI service tests (mocked)
- `test_health_routes.py` - Health check tests
- `test_ai_models.py` - AI request/response models

### Integration Tests (`tests/integration/`)
- **Real services** - Actual API calls
- **Slower** - Network latency
- **Credentials required** - Need API keys
- **Run manually** - Not in CI (unless secrets configured)

**Naming convention:** `test_{service}_service.py` or `test_{feature}_e2e.py`

## Adding New Tests

### For a new route
```python
# tests/unit/test_new_routes.py
def test_new_endpoint_success(client):
    response = client.get("/new")
    assert response.status_code == 200
```

### For a new service
```python
# tests/unit/test_new_service.py
@patch("app.services.new_service.SomeClient")
async def test_new_service_method(mock_client):
    service = NewService()
    result = await service.do_something()
    assert result is not None
```

### For a new model
```python
# tests/unit/test_new_models.py
def test_request_model_validation():
    from app.models.new import NewRequest

    request = NewRequest(field="value")
    assert request.field == "value"
```

### For integration
```python
# tests/integration/test_new_service.py
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("API_KEY"), reason="API_KEY not set")
async def test_new_service_real():
    # Test with real API
    pass
```

## Best Practices

1. **Unit tests** - Mock external dependencies
2. **One assertion per concept** - Test one thing clearly
3. **Descriptive names** - `test_chat_returns_error_when_service_unavailable`
4. **Arrange-Act-Assert** - Clear test structure
5. **Use fixtures** - Share setup between tests
6. **Mark slow tests** - `@pytest.mark.slow`
7. **Mark integration tests** - `@pytest.mark.integration`
