"""Unit tests for User Pydantic schemas."""

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models.user import UserCreate, UserListResponse, UserResponse, UserUpdate


class TestUserCreate:
    """Tests for UserCreate schema."""

    def test_user_create_with_valid_data(self) -> None:
        """UserCreate accepts valid email and display_name."""
        user = UserCreate(email="alice@example.com", display_name="Alice")
        assert user.email == "alice@example.com"
        assert user.display_name == "Alice"

    def test_user_create_strips_whitespace_from_display_name(self) -> None:
        """UserCreate strips leading/trailing whitespace from display_name."""
        user = UserCreate(email="alice@example.com", display_name="  Alice  ")
        assert user.display_name == "Alice"

    def test_user_create_rejects_empty_display_name(self) -> None:
        """UserCreate rejects an empty display_name string."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="alice@example.com", display_name="")
        assert "min_length" in str(exc_info.value).lower() or "at least" in str(
            exc_info.value
        ).lower()

    def test_user_create_rejects_blank_display_name(self) -> None:
        """UserCreate rejects a whitespace-only display_name."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="alice@example.com", display_name="   ")
        errors = exc_info.value.errors()
        assert any("blank" in str(e["msg"]).lower() for e in errors)

    def test_user_create_rejects_display_name_over_max_length(self) -> None:
        """UserCreate rejects a display_name exceeding 255 characters."""
        with pytest.raises(ValidationError):
            UserCreate(email="alice@example.com", display_name="x" * 256)

    def test_user_create_accepts_max_length_display_name(self) -> None:
        """UserCreate accepts a display_name at exactly 255 characters."""
        user = UserCreate(email="alice@example.com", display_name="x" * 255)
        assert len(user.display_name) == 255

    def test_user_create_rejects_invalid_email(self) -> None:
        """UserCreate rejects a non-email string."""
        with pytest.raises(ValidationError):
            UserCreate(email="not-an-email", display_name="Alice")

    def test_user_create_rejects_email_without_domain(self) -> None:
        """UserCreate rejects an email without a domain part."""
        with pytest.raises(ValidationError):
            UserCreate(email="alice@", display_name="Alice")

    def test_user_create_rejects_email_without_at(self) -> None:
        """UserCreate rejects an email missing @ symbol."""
        with pytest.raises(ValidationError):
            UserCreate(email="alice.example.com", display_name="Alice")

    def test_user_create_accepts_complex_email(self) -> None:
        """UserCreate accepts a valid complex email address."""
        user = UserCreate(email="alice+tag@sub.example.com", display_name="Alice")
        assert user.email == "alice+tag@sub.example.com"

    def test_user_create_rejects_missing_email(self) -> None:
        """UserCreate requires email field."""
        with pytest.raises(ValidationError):
            UserCreate(display_name="Alice")  # type: ignore[call-arg]

    def test_user_create_rejects_missing_display_name(self) -> None:
        """UserCreate requires display_name field."""
        with pytest.raises(ValidationError):
            UserCreate(email="alice@example.com")  # type: ignore[call-arg]


class TestUserUpdate:
    """Tests for UserUpdate schema."""

    def test_user_update_with_no_fields(self) -> None:
        """UserUpdate allows all fields to be omitted."""
        user = UserUpdate()
        assert user.email is None
        assert user.display_name is None

    def test_user_update_with_email_only(self) -> None:
        """UserUpdate accepts email without display_name."""
        user = UserUpdate(email="bob@example.com")
        assert user.email == "bob@example.com"
        assert user.display_name is None

    def test_user_update_with_display_name_only(self) -> None:
        """UserUpdate accepts display_name without email."""
        user = UserUpdate(display_name="Bob")
        assert user.display_name == "Bob"
        assert user.email is None

    def test_user_update_with_both_fields(self) -> None:
        """UserUpdate accepts both email and display_name."""
        user = UserUpdate(email="bob@example.com", display_name="Bob")
        assert user.email == "bob@example.com"
        assert user.display_name == "Bob"

    def test_user_update_rejects_invalid_email(self) -> None:
        """UserUpdate rejects a non-email string."""
        with pytest.raises(ValidationError):
            UserUpdate(email="not-an-email")

    def test_user_update_rejects_blank_display_name(self) -> None:
        """UserUpdate rejects whitespace-only display_name."""
        with pytest.raises(ValidationError):
            UserUpdate(display_name="   ")

    def test_user_update_strips_whitespace_from_display_name(self) -> None:
        """UserUpdate strips leading/trailing whitespace from display_name."""
        user = UserUpdate(display_name="  Bob  ")
        assert user.display_name == "Bob"


class TestUserResponse:
    """Tests for UserResponse schema."""

    def test_user_response_from_dict(self) -> None:
        """UserResponse constructs from a dictionary."""
        now = datetime.now(tz=timezone.utc)
        user_id = uuid.uuid4()
        resp = UserResponse(
            id=user_id,
            email="alice@example.com",
            display_name="Alice",
            created_at=now,
            updated_at=now,
        )
        assert resp.id == user_id
        assert resp.email == "alice@example.com"
        assert resp.display_name == "Alice"
        assert resp.created_at == now
        assert resp.updated_at == now

    def test_user_response_includes_updated_at(self) -> None:
        """UserResponse includes both created_at and updated_at timestamps."""
        created = datetime(2024, 1, 1, tzinfo=timezone.utc)
        updated = datetime(2024, 6, 15, tzinfo=timezone.utc)
        resp = UserResponse(
            id=uuid.uuid4(),
            email="alice@example.com",
            display_name="Alice",
            created_at=created,
            updated_at=updated,
        )
        assert resp.created_at == created
        assert resp.updated_at == updated


class TestUserListResponse:
    """Tests for UserListResponse schema."""

    def test_user_list_response_with_items(self) -> None:
        """UserListResponse builds from a list of UserResponse objects."""
        now = datetime.now(tz=timezone.utc)
        items = [
            UserResponse(
                id=uuid.uuid4(),
                email="alice@example.com",
                display_name="Alice",
                created_at=now,
                updated_at=now,
            ),
            UserResponse(
                id=uuid.uuid4(),
                email="bob@example.com",
                display_name="Bob",
                created_at=now,
                updated_at=now,
            ),
        ]
        resp = UserListResponse(items=items, total=10, limit=20, offset=0)
        assert len(resp.items) == 2
        assert resp.total == 10
        assert resp.limit == 20
        assert resp.offset == 0

    def test_user_list_response_empty(self) -> None:
        """UserListResponse works with no items."""
        resp = UserListResponse(items=[], total=0, limit=20, offset=0)
        assert resp.items == []
        assert resp.total == 0
