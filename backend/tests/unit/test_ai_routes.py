"""Unit tests for AI endpoints - mock OpenAI calls."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import OpenAIError

from app.main import app
from app.routes.ai import get_openai_service


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(content="Hello! I'm here to help with Mnemos."),
        )
    ]
    mock_response.model = "gpt-4o-mini"
    mock_response.usage = MagicMock(total_tokens=42)
    return mock_response


@patch("app.services.openai_service.AsyncOpenAI")
def test_chat_success(mock_openai_class, client, mock_openai_key, mock_openai_response):
    """Test successful chat completion."""
    # Setup mock
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
    mock_openai_class.return_value = mock_client

    # Make request
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "Hello", "model": "gpt-4o-mini"},
    )

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Hello! I'm here to help with Mnemos."
    assert data["model"] == "gpt-4o-mini"
    assert data["tokens_used"] == 42


def test_chat_without_api_key(client):
    """Test chat endpoint without OpenAI API key configured."""
    # Override the dependency
    mock_service = MagicMock()
    mock_service.is_available = False
    app.dependency_overrides[get_openai_service] = lambda: mock_service

    try:
    response = client.post(
            "/api/v1/ai/chat",
        json={"message": "Hello"},
    )

        assert response.status_code == 503
        assert "not available" in response.json()["detail"].lower()
    finally:
        # Clean up
        app.dependency_overrides.clear()


@patch("app.services.openai_service.AsyncOpenAI")
def test_chat_openai_error(mock_openai_class, client, mock_openai_key):
    """Test handling of OpenAI API errors."""
    # Setup mock to raise OpenAIError
    mock_client = AsyncMock()
    # Create a proper OpenAIError instance
    error = OpenAIError("API Error")
    mock_client.chat.completions.create = AsyncMock(
        side_effect=error,
    )
    mock_openai_class.return_value = mock_client

    # Make request
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "Hello"},
    )

    # Should return 502 with error message (external service error)
    assert response.status_code == 502
    data = response.json()
    assert "detail" in data
    assert "external" in data["detail"].lower() or "service" in data["detail"].lower()


def test_chat_request_validation(client, mock_openai_key):
    """Test request validation for chat endpoint."""
    # Empty message
    response = client.post("/api/v1/ai/chat", json={"message": ""})
    assert response.status_code == 422  # Validation error

    # Missing message field
    response = client.post("/api/v1/ai/chat", json={})
    assert response.status_code == 422
