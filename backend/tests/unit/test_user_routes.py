"""Unit tests for User CRUD API routes with mocked service layer."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.main import app
from app.routes.users import get_user_service


@pytest.fixture
def mock_user_service() -> AsyncMock:
    """Create a mock UserService."""
    return AsyncMock()


@pytest.fixture(autouse=True)
def override_user_service(mock_user_service: AsyncMock):
    """Override the user service dependency for all route tests."""
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    yield
    app.dependency_overrides.pop(get_user_service, None)


def _make_mock_user(
    user_id: uuid.UUID | None = None,
    email: str = "alice@example.com",
    display_name: str = "Alice",
) -> MagicMock:
    """Build a mock User ORM object with from_attributes-compatible attributes."""
    user = MagicMock()
    user.id = user_id or uuid.uuid4()
    user.email = email
    user.display_name = display_name
    user.created_at = datetime.now(tz=timezone.utc)
    user.updated_at = datetime.now(tz=timezone.utc)
    return user


class TestCreateUserRoute:
    """Tests for POST /api/v1/users."""

    def test_create_user_success(self, client, mock_user_service: AsyncMock) -> None:
        """POST /api/v1/users creates a user and returns 201."""
        mock_user = _make_mock_user(email="alice@example.com", display_name="Alice")
        mock_user_service.create_user.return_value = mock_user

        response = client.post(
            "/api/v1/users",
            json={"email": "alice@example.com", "display_name": "Alice"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "alice@example.com"
        assert data["display_name"] == "Alice"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_user_duplicate_email_returns_409(
        self, client, mock_user_service: AsyncMock
    ) -> None:
        """POST /api/v1/users returns 409 on duplicate email."""
        mock_user_service.create_user.side_effect = IntegrityError(
            "duplicate", params=None, orig=Exception()
        )

        response = client.post(
            "/api/v1/users",
            json={"email": "dup@example.com", "display_name": "Dup"},
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_user_invalid_email_returns_422(self, client) -> None:
        """POST /api/v1/users returns 422 on invalid email."""
        response = client.post(
            "/api/v1/users",
            json={"email": "not-an-email", "display_name": "Alice"},
        )

        assert response.status_code == 422

    def test_create_user_missing_fields_returns_422(self, client) -> None:
        """POST /api/v1/users returns 422 when required fields are missing."""
        response = client.post("/api/v1/users", json={})

        assert response.status_code == 422

    def test_create_user_blank_display_name_returns_422(self, client) -> None:
        """POST /api/v1/users returns 422 for blank display_name."""
        response = client.post(
            "/api/v1/users",
            json={"email": "alice@example.com", "display_name": "   "},
        )

        assert response.status_code == 422


class TestListUsersRoute:
    """Tests for GET /api/v1/users."""

    def test_list_users_success(self, client, mock_user_service: AsyncMock) -> None:
        """GET /api/v1/users returns paginated user list."""
        users = [
            _make_mock_user(email="alice@example.com"),
            _make_mock_user(email="bob@example.com"),
        ]
        mock_user_service.list_users.return_value = (users, 2)

        response = client.get("/api/v1/users")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2
        assert data["limit"] == 20
        assert data["offset"] == 0

    def test_list_users_with_pagination(
        self, client, mock_user_service: AsyncMock
    ) -> None:
        """GET /api/v1/users respects limit and offset query params."""
        mock_user_service.list_users.return_value = ([], 5)

        response = client.get("/api/v1/users?limit=10&offset=3")

        assert response.status_code == 200
        mock_user_service.list_users.assert_awaited_once_with(limit=10, offset=3)

    def test_list_users_empty(self, client, mock_user_service: AsyncMock) -> None:
        """GET /api/v1/users returns empty list when no users exist."""
        mock_user_service.list_users.return_value = ([], 0)

        response = client.get("/api/v1/users")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0


class TestGetUserRoute:
    """Tests for GET /api/v1/users/{user_id}."""

    def test_get_user_success(self, client, mock_user_service: AsyncMock) -> None:
        """GET /api/v1/users/{id} returns the user."""
        user_id = uuid.uuid4()
        mock_user = _make_mock_user(
            user_id=user_id, email="alice@example.com", display_name="Alice"
        )
        mock_user_service.get_user.return_value = mock_user

        response = client.get(f"/api/v1/users/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "alice@example.com"
        assert data["display_name"] == "Alice"

    def test_get_user_not_found(self, client, mock_user_service: AsyncMock) -> None:
        """GET /api/v1/users/{id} returns 404 for non-existent user."""
        mock_user_service.get_user.return_value = None

        response = client.get(f"/api/v1/users/{uuid.uuid4()}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_user_invalid_uuid(self, client) -> None:
        """GET /api/v1/users/{id} returns 422 for invalid UUID."""
        response = client.get("/api/v1/users/not-a-uuid")

        assert response.status_code == 422


class TestUpdateUserRoute:
    """Tests for PATCH /api/v1/users/{user_id}."""

    def test_update_user_success(self, client, mock_user_service: AsyncMock) -> None:
        """PATCH /api/v1/users/{id} updates the user."""
        user_id = uuid.uuid4()
        mock_user = _make_mock_user(user_id=user_id, display_name="Updated")
        mock_user_service.update_user.return_value = mock_user

        response = client.patch(
            f"/api/v1/users/{user_id}",
            json={"display_name": "Updated"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Updated"

    def test_update_user_email(self, client, mock_user_service: AsyncMock) -> None:
        """PATCH /api/v1/users/{id} can update email."""
        user_id = uuid.uuid4()
        mock_user = _make_mock_user(user_id=user_id, email="new@example.com")
        mock_user_service.update_user.return_value = mock_user

        response = client.patch(
            f"/api/v1/users/{user_id}",
            json={"email": "new@example.com"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "new@example.com"

    def test_update_user_not_found(self, client, mock_user_service: AsyncMock) -> None:
        """PATCH /api/v1/users/{id} returns 404 for non-existent user."""
        mock_user_service.update_user.return_value = None

        response = client.patch(
            f"/api/v1/users/{uuid.uuid4()}",
            json={"display_name": "New"},
        )

        assert response.status_code == 404

    def test_update_user_duplicate_email_returns_409(
        self, client, mock_user_service: AsyncMock
    ) -> None:
        """PATCH /api/v1/users/{id} returns 409 on duplicate email."""
        mock_user_service.update_user.side_effect = IntegrityError(
            "duplicate", params=None, orig=Exception()
        )

        response = client.patch(
            f"/api/v1/users/{uuid.uuid4()}",
            json={"email": "taken@example.com"},
        )

        assert response.status_code == 409


class TestDeleteUserRoute:
    """Tests for DELETE /api/v1/users/{user_id}."""

    def test_delete_user_success(self, client, mock_user_service: AsyncMock) -> None:
        """DELETE /api/v1/users/{id} deletes the user and returns 204."""
        mock_user_service.delete_user.return_value = True

        response = client.delete(f"/api/v1/users/{uuid.uuid4()}")

        assert response.status_code == 204

    def test_delete_user_not_found(self, client, mock_user_service: AsyncMock) -> None:
        """DELETE /api/v1/users/{id} returns 404 for non-existent user."""
        mock_user_service.delete_user.return_value = False

        response = client.delete(f"/api/v1/users/{uuid.uuid4()}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
