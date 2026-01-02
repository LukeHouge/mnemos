"""Unit tests for OpenAI service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import settings
from app.services.openai_service import OpenAIService


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(content="Test response"),
        )
    ]
    mock_response.model = "gpt-4o-mini"
    mock_response.usage = MagicMock(total_tokens=42)
    return mock_response


@patch("app.services.openai_service.AsyncOpenAI")
def test_openai_service_initialization_with_key(mock_openai_class, mock_openai_key):
    """Test service initializes correctly with API key."""
    service = OpenAIService()
    assert service.is_available is True


@patch.object(settings, "OPENAI_API_KEY", None)
def test_openai_service_initialization_without_key():
    """Test service initializes correctly without API key."""
    service = OpenAIService()
    assert service.is_available is False


@patch("app.services.openai_service.AsyncOpenAI")
async def test_chat_completion_success(mock_openai_class, mock_openai_key, mock_openai_response):
    """Test successful chat completion."""
    # Setup mock
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
    mock_openai_class.return_value = mock_client

    # Create service and call
    service = OpenAIService()
    content, model, tokens = await service.chat_completion("Hello")

    # Assertions
    assert content == "Test response"
    assert model == "gpt-4o-mini"
    assert tokens == 42


@patch.object(settings, "OPENAI_API_KEY", None)
async def test_chat_completion_without_api_key():
    """Test chat completion raises error without API key."""
    service = OpenAIService()

    with pytest.raises(ValueError, match="AI service not available"):
        await service.chat_completion("Hello")


@patch("app.services.openai_service.AsyncOpenAI")
async def test_test_connection_success(mock_openai_class, mock_openai_key):
    """Test successful connection test."""
    # Setup mock
    mock_client = AsyncMock()
    mock_client.models.list = AsyncMock()
    mock_openai_class.return_value = mock_client

    # Create service and test
    service = OpenAIService()
    success, message = await service.test_connection()

    assert success is True
    assert "successfully" in message.lower()


@patch.object(settings, "OPENAI_API_KEY", None)
async def test_test_connection_without_key():
    """Test connection test without API key."""
    service = OpenAIService()
    success, message = await service.test_connection()

    assert success is False
    assert "not configured" in message.lower()
