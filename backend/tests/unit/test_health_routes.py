"""Unit tests for health check endpoints."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.health import OverallHealthStatusEnum, ServiceHealthStatusEnum
from app.routes.health import get_openai_service

client = TestClient(app)


def test_basic_health_check(client):
    """Test basic health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == OverallHealthStatusEnum.HEALTHY.value
    assert data["version"] == "1.0.0"


@patch("app.routes.health.check_db_connection")
def test_full_health_check_without_openai_key(mock_db_check, client):
    """Test detailed health check when OpenAI is not configured."""
    mock_db_check.return_value = (True, "Connected successfully")

    # Override the dependency
    mock_service = MagicMock()
    mock_service.is_available = False
    app.dependency_overrides[get_openai_service] = lambda: mock_service

    try:
        response = client.get("/api/v1/health/full")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        assert "openai" in data["services"]
        assert data["services"]["openai"]["status"] == ServiceHealthStatusEnum.NOT_CONFIGURED.value
        assert "postgres" in data["services"]
        assert data["services"]["postgres"]["status"] == ServiceHealthStatusEnum.CONNECTED.value
    finally:
        # Clean up
        app.dependency_overrides.clear()


@patch("app.routes.health.check_db_connection")
def test_full_health_check_with_db_error(mock_db_check, client):
    """Test detailed health check when database is unreachable."""
    mock_db_check.return_value = (False, "Connection failed: ConnectionRefusedError")

    mock_service = MagicMock()
    mock_service.is_available = False
    app.dependency_overrides[get_openai_service] = lambda: mock_service

    try:
        response = client.get("/api/v1/health/full")
        assert response.status_code == 200
        data = response.json()
        assert data["services"]["postgres"]["status"] == ServiceHealthStatusEnum.ERROR.value
        assert data["status"] == OverallHealthStatusEnum.DEGRADED.value
    finally:
        app.dependency_overrides.clear()


def test_intentional_failure_for_ci_check() -> None:
    """INTENTIONAL FAILURE: This test exists to verify CI catches failures."""
    assert 1 == 2, "This test is intentionally failing to verify CI health checks"
