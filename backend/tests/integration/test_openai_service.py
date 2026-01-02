"""Integration tests for AI endpoints - uses actual OpenAI API."""

import os

import pytest

from app.models.common import ServiceStatusEnum


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
def test_openai_connection_real():
    """Test actual connection to OpenAI API."""
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Simple API call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say 'test successful' and nothing else"}],
        max_tokens=10,
    )

    assert response.choices[0].message.content
    assert "test" in response.choices[0].message.content.lower()


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
def test_chat_endpoint_real(client):
    """Test chat endpoint with real OpenAI API."""
    response = client.post(
        "/api/v1/ai/chat",
        json={
            "message": "Say 'integration test passed' and nothing else",
            "model": "gpt-4o-mini",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["tokens_used"] > 0
    assert "integration" in data["response"].lower() or "test" in data["response"].lower()


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
def test_openai_test_endpoint_real(client):
    """Test OpenAI connection test endpoint with real API."""
    response = client.get("/api/v1/ai/test")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] in [ServiceStatusEnum.AVAILABLE.value, ServiceStatusEnum.ERROR.value]

    if data["status"] == ServiceStatusEnum.AVAILABLE.value:
        assert "success" in data["message"].lower() or "connected" in data["message"].lower()
