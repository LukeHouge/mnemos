from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services import openai_service


@pytest.fixture(autouse=True)
def clear_openai_singleton():
    """Automatically clear OpenAI service singleton before and after each test."""
    # Clear singleton before test to ensure fresh state
    openai_service._openai_service = None
    yield
    # Clear singleton after test to prevent test pollution
    openai_service._openai_service = None


@pytest.fixture
def client():
    """Test client for API testing."""
    return TestClient(app)


@pytest.fixture
def mock_openai_key():
    """Set a mock OpenAI API key for testing."""
    with patch.object(settings, "OPENAI_API_KEY", "sk-test-key-123"):
        yield
