"""Unit tests for health check endpoints."""

from unittest.mock import MagicMock

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


def test_full_health_check_without_openai_key(client):
    """Test detailed health check when OpenAI is not configured."""
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
    finally:
        # Clean up
        app.dependency_overrides.clear()
