"""Unit tests for memo route handlers."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.main import app
from app.models.memo import MemoListResponse, MemoResponse
from app.routes.memos import _get_memo_service


@pytest.fixture
def memo_response():
    """A sample MemoResponse for test assertions."""
    return MemoResponse(
        id=uuid.UUID("12345678-1234-5678-1234-567812345678"),
        title="Test Memo",
        content="Hello world",
        tags=["test"],
        created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def mock_service(memo_response):
    """Provide a mock MemoService and wire it into the app."""
    service = AsyncMock()
    service.create_memo = AsyncMock(return_value=memo_response)
    service.get_memo = AsyncMock(return_value=memo_response)
    service.list_memos = AsyncMock(
        return_value=MemoListResponse(memos=[memo_response], total=1)
    )
    service.update_memo = AsyncMock(return_value=memo_response)
    service.delete_memo = AsyncMock(return_value=True)

    app.dependency_overrides[_get_memo_service] = lambda: service
    yield service
    app.dependency_overrides.pop(_get_memo_service, None)


class TestCreateMemo:
    """Tests for POST /api/v1/memos."""

    def test_create_memo_success(self, client, mock_service):
        """Successful memo creation returns 201."""
        response = client.post(
            "/api/v1/memos",
            json={"content": "Hello world", "title": "Test Memo", "tags": ["test"]},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Hello world"
        assert data["title"] == "Test Memo"
        mock_service.create_memo.assert_awaited_once()

    def test_create_memo_minimal(self, client, mock_service):
        """Memo can be created with content only."""
        response = client.post(
            "/api/v1/memos",
            json={"content": "Just a note"},
        )
        assert response.status_code == 201
        mock_service.create_memo.assert_awaited_once()

    def test_create_memo_validation_error(self, client, mock_service):
        """Empty content returns 422."""
        response = client.post("/api/v1/memos", json={"content": ""})
        assert response.status_code == 422

    def test_create_memo_missing_content(self, client, mock_service):
        """Missing content field returns 422."""
        response = client.post("/api/v1/memos", json={})
        assert response.status_code == 422


class TestGetMemo:
    """Tests for GET /api/v1/memos/{memo_id}."""

    def test_get_memo_success(self, client, mock_service):
        """Existing memo returns 200."""
        memo_id = "12345678-1234-5678-1234-567812345678"
        response = client.get(f"/api/v1/memos/{memo_id}")
        assert response.status_code == 200
        assert response.json()["id"] == memo_id

    def test_get_memo_not_found(self, client, mock_service):
        """Missing memo returns 404."""
        mock_service.get_memo = AsyncMock(return_value=None)
        memo_id = uuid.uuid4()
        response = client.get(f"/api/v1/memos/{memo_id}")
        assert response.status_code == 404

    def test_get_memo_invalid_uuid(self, client, mock_service):
        """Invalid UUID returns 422."""
        response = client.get("/api/v1/memos/not-a-uuid")
        assert response.status_code == 422


class TestListMemos:
    """Tests for GET /api/v1/memos."""

    def test_list_memos_success(self, client, mock_service):
        """List endpoint returns memos and total."""
        response = client.get("/api/v1/memos")
        assert response.status_code == 200
        data = response.json()
        assert "memos" in data
        assert "total" in data
        assert data["total"] == 1

    def test_list_memos_with_tag_filter(self, client, mock_service):
        """Tag query parameter is forwarded to service."""
        response = client.get("/api/v1/memos?tag=shopping")
        assert response.status_code == 200
        mock_service.list_memos.assert_awaited_once_with(
            tag="shopping", search=None, offset=0, limit=50
        )

    def test_list_memos_with_search(self, client, mock_service):
        """Search query parameter is forwarded to service."""
        response = client.get("/api/v1/memos?search=groceries")
        assert response.status_code == 200
        mock_service.list_memos.assert_awaited_once_with(
            tag=None, search="groceries", offset=0, limit=50
        )

    def test_list_memos_pagination(self, client, mock_service):
        """Offset and limit query parameters are forwarded."""
        response = client.get("/api/v1/memos?offset=10&limit=5")
        assert response.status_code == 200
        mock_service.list_memos.assert_awaited_once_with(
            tag=None, search=None, offset=10, limit=5
        )


class TestUpdateMemo:
    """Tests for PATCH /api/v1/memos/{memo_id}."""

    def test_update_memo_success(self, client, mock_service):
        """Successful update returns 200."""
        memo_id = "12345678-1234-5678-1234-567812345678"
        response = client.patch(
            f"/api/v1/memos/{memo_id}",
            json={"content": "Updated content"},
        )
        assert response.status_code == 200
        mock_service.update_memo.assert_awaited_once()

    def test_update_memo_not_found(self, client, mock_service):
        """Update on missing memo returns 404."""
        mock_service.update_memo = AsyncMock(return_value=None)
        memo_id = uuid.uuid4()
        response = client.patch(
            f"/api/v1/memos/{memo_id}",
            json={"content": "Updated"},
        )
        assert response.status_code == 404


class TestDeleteMemo:
    """Tests for DELETE /api/v1/memos/{memo_id}."""

    def test_delete_memo_success(self, client, mock_service):
        """Successful delete returns 204."""
        memo_id = uuid.uuid4()
        response = client.delete(f"/api/v1/memos/{memo_id}")
        assert response.status_code == 204

    def test_delete_memo_not_found(self, client, mock_service):
        """Delete on missing memo returns 404."""
        mock_service.delete_memo = AsyncMock(return_value=False)
        memo_id = uuid.uuid4()
        response = client.delete(f"/api/v1/memos/{memo_id}")
        assert response.status_code == 404
