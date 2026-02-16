"""Unit tests for memo Pydantic models."""

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models.memo import MemoCreate, MemoListResponse, MemoResponse, MemoUpdate


class TestMemoCreate:
    """Tests for MemoCreate request model."""

    def test_create_with_content_only(self):
        """Minimal valid memo requires only content."""
        memo = MemoCreate(content="Buy groceries")
        assert memo.content == "Buy groceries"
        assert memo.title is None
        assert memo.tags == []

    def test_create_with_all_fields(self):
        """All fields can be provided."""
        memo = MemoCreate(
            title="Shopping",
            content="Buy groceries",
            tags=["shopping", "personal"],
        )
        assert memo.title == "Shopping"
        assert memo.content == "Buy groceries"
        assert memo.tags == ["shopping", "personal"]

    def test_create_rejects_empty_content(self):
        """Content must not be empty."""
        with pytest.raises(ValidationError):
            MemoCreate(content="")

    def test_create_rejects_missing_content(self):
        """Content is required."""
        with pytest.raises(ValidationError):
            MemoCreate()  # type: ignore[call-arg]


class TestMemoUpdate:
    """Tests for MemoUpdate request model."""

    def test_update_all_fields_optional(self):
        """All fields are optional for partial updates."""
        update = MemoUpdate()
        assert update.title is None
        assert update.content is None
        assert update.tags is None

    def test_update_with_content(self):
        """Content can be updated alone."""
        update = MemoUpdate(content="Updated note")
        assert update.content == "Updated note"

    def test_update_rejects_empty_content(self):
        """Content, if provided, must not be empty."""
        with pytest.raises(ValidationError):
            MemoUpdate(content="")

    def test_update_exclude_unset(self):
        """model_dump(exclude_unset=True) only returns provided fields."""
        update = MemoUpdate(content="New text")
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {"content": "New text"}


class TestMemoResponse:
    """Tests for MemoResponse model."""

    def test_response_serialization(self):
        """MemoResponse serializes all fields correctly."""
        now = datetime.now(tz=timezone.utc)
        memo_id = uuid.uuid4()
        resp = MemoResponse(
            id=memo_id,
            title="Test",
            content="Hello world",
            tags=["test"],
            created_at=now,
            updated_at=now,
        )
        data = resp.model_dump()
        assert data["id"] == memo_id
        assert data["title"] == "Test"
        assert data["content"] == "Hello world"
        assert data["tags"] == ["test"]

    def test_response_title_optional(self):
        """Title may be None."""
        now = datetime.now(tz=timezone.utc)
        resp = MemoResponse(
            id=uuid.uuid4(),
            title=None,
            content="No title",
            tags=[],
            created_at=now,
            updated_at=now,
        )
        assert resp.title is None


class TestMemoListResponse:
    """Tests for MemoListResponse model."""

    def test_list_response(self):
        """MemoListResponse wraps a list and total count."""
        now = datetime.now(tz=timezone.utc)
        memo = MemoResponse(
            id=uuid.uuid4(),
            title="A",
            content="B",
            tags=[],
            created_at=now,
            updated_at=now,
        )
        resp = MemoListResponse(memos=[memo], total=1)
        assert len(resp.memos) == 1
        assert resp.total == 1

    def test_list_response_empty(self):
        """Empty list is valid."""
        resp = MemoListResponse(memos=[], total=0)
        assert resp.memos == []
        assert resp.total == 0
