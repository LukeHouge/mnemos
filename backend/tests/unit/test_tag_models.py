"""Unit tests for Tag Pydantic schemas."""

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models.tag import TagCreate, TagListResponse, TagResponse, TagUpdate


class TestTagCreate:
    """Tests for TagCreate schema."""

    def test_tag_create_with_name_only(self) -> None:
        """TagCreate accepts a name without a color."""
        tag = TagCreate(name="receipts")
        assert tag.name == "receipts"
        assert tag.color is None

    def test_tag_create_with_name_and_color(self) -> None:
        """TagCreate accepts name and valid hex color."""
        tag = TagCreate(name="receipts", color="#FF5733")
        assert tag.name == "receipts"
        assert tag.color == "#FF5733"

    def test_tag_create_strips_whitespace_from_name(self) -> None:
        """TagCreate strips leading/trailing whitespace from name."""
        tag = TagCreate(name="  receipts  ")
        assert tag.name == "receipts"

    def test_tag_create_rejects_empty_name(self) -> None:
        """TagCreate rejects an empty name string."""
        with pytest.raises(ValidationError) as exc_info:
            TagCreate(name="")
        assert "min_length" in str(exc_info.value).lower() or "at least" in str(
            exc_info.value
        ).lower()

    def test_tag_create_rejects_blank_name(self) -> None:
        """TagCreate rejects a whitespace-only name."""
        with pytest.raises(ValidationError) as exc_info:
            TagCreate(name="   ")
        errors = exc_info.value.errors()
        assert any("blank" in str(e["msg"]).lower() for e in errors)

    def test_tag_create_rejects_name_over_max_length(self) -> None:
        """TagCreate rejects a name exceeding 100 characters."""
        with pytest.raises(ValidationError):
            TagCreate(name="x" * 101)

    def test_tag_create_rejects_invalid_color_format(self) -> None:
        """TagCreate rejects non-hex color strings."""
        with pytest.raises(ValidationError) as exc_info:
            TagCreate(name="test", color="red")
        errors = exc_info.value.errors()
        assert any("hex" in str(e["msg"]).lower() for e in errors)

    def test_tag_create_rejects_short_hex_color(self) -> None:
        """TagCreate rejects 3-digit hex shorthand."""
        with pytest.raises(ValidationError):
            TagCreate(name="test", color="#F00")

    def test_tag_create_rejects_color_without_hash(self) -> None:
        """TagCreate rejects hex color missing leading #."""
        with pytest.raises(ValidationError):
            TagCreate(name="test", color="FF5733")

    def test_tag_create_accepts_lowercase_hex_color(self) -> None:
        """TagCreate accepts lowercase hex color digits."""
        tag = TagCreate(name="test", color="#abcdef")
        assert tag.color == "#abcdef"


class TestTagUpdate:
    """Tests for TagUpdate schema."""

    def test_tag_update_with_no_fields(self) -> None:
        """TagUpdate allows all fields to be omitted."""
        tag = TagUpdate()
        assert tag.name is None
        assert tag.color is None

    def test_tag_update_with_name_only(self) -> None:
        """TagUpdate accepts name without color."""
        tag = TagUpdate(name="invoices")
        assert tag.name == "invoices"
        assert tag.color is None

    def test_tag_update_with_color_only(self) -> None:
        """TagUpdate accepts color without name."""
        tag = TagUpdate(color="#123456")
        assert tag.name is None
        assert tag.color == "#123456"

    def test_tag_update_rejects_blank_name(self) -> None:
        """TagUpdate rejects whitespace-only name."""
        with pytest.raises(ValidationError):
            TagUpdate(name="   ")

    def test_tag_update_rejects_invalid_color(self) -> None:
        """TagUpdate rejects non-hex color."""
        with pytest.raises(ValidationError):
            TagUpdate(color="notacolor")

    def test_tag_update_strips_whitespace_from_name(self) -> None:
        """TagUpdate strips leading/trailing whitespace from name."""
        tag = TagUpdate(name="  invoices  ")
        assert tag.name == "invoices"


class TestTagResponse:
    """Tests for TagResponse schema."""

    def test_tag_response_from_dict(self) -> None:
        """TagResponse constructs from a dictionary."""
        now = datetime.now(tz=timezone.utc)
        tag_id = uuid.uuid4()
        resp = TagResponse(id=tag_id, name="receipts", color="#FF5733", created_at=now)
        assert resp.id == tag_id
        assert resp.name == "receipts"
        assert resp.color == "#FF5733"
        assert resp.created_at == now

    def test_tag_response_with_null_color(self) -> None:
        """TagResponse works with null color."""
        now = datetime.now(tz=timezone.utc)
        resp = TagResponse(id=uuid.uuid4(), name="receipts", color=None, created_at=now)
        assert resp.color is None


class TestTagListResponse:
    """Tests for TagListResponse schema."""

    def test_tag_list_response_with_items(self) -> None:
        """TagListResponse builds from a list of TagResponse objects."""
        now = datetime.now(tz=timezone.utc)
        items = [
            TagResponse(id=uuid.uuid4(), name="a", color=None, created_at=now),
            TagResponse(id=uuid.uuid4(), name="b", color="#000000", created_at=now),
        ]
        resp = TagListResponse(items=items, total=10, limit=20, offset=0)
        assert len(resp.items) == 2
        assert resp.total == 10
        assert resp.limit == 20
        assert resp.offset == 0

    def test_tag_list_response_empty(self) -> None:
        """TagListResponse works with no items."""
        resp = TagListResponse(items=[], total=0, limit=20, offset=0)
        assert resp.items == []
        assert resp.total == 0
