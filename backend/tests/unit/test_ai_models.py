"""Unit tests for AI models."""

import pytest
from pydantic import ValidationError

from app.models.ai import ChatRequest, ChatResponse


def test_chat_request_valid():
    """Test ChatRequest with valid data."""
    request = ChatRequest(message="Hello", model="gpt-4o-mini")
    assert request.message == "Hello"
    assert request.model == "gpt-4o-mini"


def test_chat_request_defaults():
    """Test ChatRequest uses default model."""
    request = ChatRequest(message="Hello")
    assert request.model == "gpt-4o-mini"


def test_chat_request_empty_message():
    """Test ChatRequest rejects empty message."""
    with pytest.raises(ValidationError):
        ChatRequest(message="")


def test_chat_response_valid():
    """Test ChatResponse with valid data."""
    response = ChatResponse(
        response="Hello back!",
        model="gpt-4o-mini",
        tokens_used=42,
    )
    assert response.response == "Hello back!"
    assert response.model == "gpt-4o-mini"
    assert response.tokens_used == 42


def test_chat_response_negative_tokens():
    """Test ChatResponse rejects negative tokens."""
    with pytest.raises(ValidationError):
        ChatResponse(
            response="Hello",
            model="gpt-4o-mini",
            tokens_used=-1,
        )
