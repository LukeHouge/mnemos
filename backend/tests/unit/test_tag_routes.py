"""Unit tests for Tag CRUD API routes with mocked service layer."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.main import app
from app.routes.tags import get_tag_service


@pytest.fixture
def mock_tag_service() -> AsyncMock:
    """Create a mock TagService."""
    return AsyncMock()


@pytest.fixture(autouse=True)
def override_tag_service(mock_tag_service: AsyncMock):
    """Override the tag service dependency for all route tests."""
    app.dependency_overrides[get_tag_service] = lambda: mock_tag_service
    yield
    app.dependency_overrides.pop(get_tag_service, None)


def _make_mock_tag(
    tag_id: uuid.UUID | None = None,
    name: str = "receipts",
    color: str | None = "#FF5733",
) -> MagicMock:
    """Build a mock Tag ORM object with from_attributes-compatible attributes."""
    tag = MagicMock()
    tag.id = tag_id or uuid.uuid4()
    tag.name = name
    tag.color = color
    tag.created_at = datetime.now(tz=timezone.utc)
    return tag


class TestCreateTagRoute:
    """Tests for POST /api/v1/tags."""

    def test_create_tag_success(self, client, mock_tag_service: AsyncMock) -> None:
        """POST /api/v1/tags creates a tag and returns 201."""
        mock_tag = _make_mock_tag(name="receipts", color="#FF5733")
        mock_tag_service.create_tag.return_value = mock_tag

        response = client.post(
            "/api/v1/tags",
            json={"name": "receipts", "color": "#FF5733"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "receipts"
        assert data["color"] == "#FF5733"
        assert "id" in data
        assert "created_at" in data

    def test_create_tag_without_color(self, client, mock_tag_service: AsyncMock) -> None:
        """POST /api/v1/tags works without color."""
        mock_tag = _make_mock_tag(name="manuals", color=None)
        mock_tag_service.create_tag.return_value = mock_tag

        response = client.post("/api/v1/tags", json={"name": "manuals"})

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "manuals"
        assert data["color"] is None

    def test_create_tag_duplicate_returns_409(
        self, client, mock_tag_service: AsyncMock
    ) -> None:
        """POST /api/v1/tags returns 409 on duplicate name."""
        mock_tag_service.create_tag.side_effect = IntegrityError(
            "duplicate", params=None, orig=Exception()
        )

        response = client.post("/api/v1/tags", json={"name": "duplicate"})

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_tag_validation_error(self, client) -> None:
        """POST /api/v1/tags returns 422 on invalid input."""
        response = client.post("/api/v1/tags", json={"name": "", "color": "notahex"})

        assert response.status_code == 422


class TestListTagsRoute:
    """Tests for GET /api/v1/tags."""

    def test_list_tags_success(self, client, mock_tag_service: AsyncMock) -> None:
        """GET /api/v1/tags returns paginated tag list."""
        tags = [_make_mock_tag(name="a"), _make_mock_tag(name="b")]
        mock_tag_service.list_tags.return_value = (tags, 2)

        response = client.get("/api/v1/tags")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2
        assert data["limit"] == 20
        assert data["offset"] == 0

    def test_list_tags_with_pagination(self, client, mock_tag_service: AsyncMock) -> None:
        """GET /api/v1/tags respects limit and offset query params."""
        mock_tag_service.list_tags.return_value = ([], 5)

        response = client.get("/api/v1/tags?limit=10&offset=3")

        assert response.status_code == 200
        mock_tag_service.list_tags.assert_awaited_once_with(limit=10, offset=3)

    def test_list_tags_empty(self, client, mock_tag_service: AsyncMock) -> None:
        """GET /api/v1/tags returns empty list when no tags exist."""
        mock_tag_service.list_tags.return_value = ([], 0)

        response = client.get("/api/v1/tags")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0


class TestGetTagRoute:
    """Tests for GET /api/v1/tags/{tag_id}."""

    def test_get_tag_success(self, client, mock_tag_service: AsyncMock) -> None:
        """GET /api/v1/tags/{id} returns the tag."""
        tag_id = uuid.uuid4()
        mock_tag = _make_mock_tag(tag_id=tag_id, name="receipts")
        mock_tag_service.get_tag.return_value = mock_tag

        response = client.get(f"/api/v1/tags/{tag_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "receipts"

    def test_get_tag_not_found(self, client, mock_tag_service: AsyncMock) -> None:
        """GET /api/v1/tags/{id} returns 404 for non-existent tag."""
        mock_tag_service.get_tag.return_value = None

        response = client.get(f"/api/v1/tags/{uuid.uuid4()}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_tag_invalid_uuid(self, client) -> None:
        """GET /api/v1/tags/{id} returns 422 for invalid UUID."""
        response = client.get("/api/v1/tags/not-a-uuid")

        assert response.status_code == 422


class TestUpdateTagRoute:
    """Tests for PATCH /api/v1/tags/{tag_id}."""

    def test_update_tag_success(self, client, mock_tag_service: AsyncMock) -> None:
        """PATCH /api/v1/tags/{id} updates the tag."""
        tag_id = uuid.uuid4()
        mock_tag = _make_mock_tag(tag_id=tag_id, name="updated")
        mock_tag_service.update_tag.return_value = mock_tag

        response = client.patch(
            f"/api/v1/tags/{tag_id}",
            json={"name": "updated"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "updated"

    def test_update_tag_not_found(self, client, mock_tag_service: AsyncMock) -> None:
        """PATCH /api/v1/tags/{id} returns 404 for non-existent tag."""
        mock_tag_service.update_tag.return_value = None

        response = client.patch(
            f"/api/v1/tags/{uuid.uuid4()}",
            json={"name": "new"},
        )

        assert response.status_code == 404

    def test_update_tag_duplicate_returns_409(
        self, client, mock_tag_service: AsyncMock
    ) -> None:
        """PATCH /api/v1/tags/{id} returns 409 on duplicate name."""
        mock_tag_service.update_tag.side_effect = IntegrityError(
            "duplicate", params=None, orig=Exception()
        )

        response = client.patch(
            f"/api/v1/tags/{uuid.uuid4()}",
            json={"name": "taken"},
        )

        assert response.status_code == 409


class TestDeleteTagRoute:
    """Tests for DELETE /api/v1/tags/{tag_id}."""

    def test_delete_tag_success(self, client, mock_tag_service: AsyncMock) -> None:
        """DELETE /api/v1/tags/{id} deletes the tag and returns 204."""
        mock_tag_service.delete_tag.return_value = True

        response = client.delete(f"/api/v1/tags/{uuid.uuid4()}")

        assert response.status_code == 204

    def test_delete_tag_not_found(self, client, mock_tag_service: AsyncMock) -> None:
        """DELETE /api/v1/tags/{id} returns 404 for non-existent tag."""
        mock_tag_service.delete_tag.return_value = False

        response = client.delete(f"/api/v1/tags/{uuid.uuid4()}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
