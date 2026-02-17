"""Unit tests for image endpoints."""

import io
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

from app.db.base import get_session
from app.main import app
from app.services.image_service import get_image_service


def _mock_image(image_id: uuid.UUID | None = None, owner_id: uuid.UUID | None = None) -> MagicMock:
    """Create a mock Image ORM object."""
    now = datetime.now(tz=UTC)
    img = MagicMock()
    img.id = image_id or uuid.uuid4()
    img.filename = "test.png"
    img.description = "A test image"
    img.mime_type = "image/png"
    img.file_size_bytes = 1024
    img.extracted_text = None
    img.owner_id = owner_id or uuid.uuid4()
    img.created_at = now
    img.updated_at = now
    return img


def test_upload_image_success(client):
    """Test successful image upload."""
    owner_id = uuid.uuid4()
    mock_service = MagicMock()
    mock_img = _mock_image(owner_id=owner_id)
    mock_service.upload_image = AsyncMock(return_value=mock_img)

    mock_session = AsyncMock()

    app.dependency_overrides[get_image_service] = lambda: mock_service
    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        response = client.post(
            f"/api/v1/images?owner_id={owner_id}",
            files={"file": ("test.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "test.png"
        assert data["mime_type"] == "image/png"
    finally:
        app.dependency_overrides.clear()


def test_upload_image_non_image_content_type(client):
    """Test upload rejects non-image files."""
    owner_id = uuid.uuid4()
    mock_session = AsyncMock()
    mock_service = MagicMock()

    app.dependency_overrides[get_image_service] = lambda: mock_service
    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        response = client.post(
            f"/api/v1/images?owner_id={owner_id}",
            files={"file": ("file.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        assert response.status_code == 400
        assert "image" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


def test_upload_image_service_value_error(client):
    """Test upload returns 400 when service raises ValueError."""
    owner_id = uuid.uuid4()
    mock_service = MagicMock()
    mock_service.upload_image = AsyncMock(
        side_effect=ValueError("Unsupported image type: image/bmp")
    )

    mock_session = AsyncMock()

    app.dependency_overrides[get_image_service] = lambda: mock_service
    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        response = client.post(
            f"/api/v1/images?owner_id={owner_id}",
            files={"file": ("test.bmp", io.BytesIO(b"\x00" * 10), "image/bmp")},
        )
        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()


def test_get_image_success(client):
    """Test retrieving image metadata."""
    mock_img = _mock_image()
    mock_service = MagicMock()
    mock_service.get_image = AsyncMock(return_value=mock_img)

    mock_session = AsyncMock()

    app.dependency_overrides[get_image_service] = lambda: mock_service
    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        response = client.get(f"/api/v1/images/{mock_img.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.png"
    finally:
        app.dependency_overrides.clear()


def test_get_image_not_found(client):
    """Test 404 for non-existent image."""
    mock_service = MagicMock()
    mock_service.get_image = AsyncMock(return_value=None)

    mock_session = AsyncMock()

    app.dependency_overrides[get_image_service] = lambda: mock_service
    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        response = client.get(f"/api/v1/images/{uuid.uuid4()}")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_list_images_success(client):
    """Test listing images for an owner."""
    owner_id = uuid.uuid4()
    mock_imgs = [_mock_image(owner_id=owner_id), _mock_image(owner_id=owner_id)]
    mock_service = MagicMock()
    mock_service.list_images = AsyncMock(return_value=(mock_imgs, 2))

    mock_session = AsyncMock()

    app.dependency_overrides[get_image_service] = lambda: mock_service
    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        response = client.get(f"/api/v1/images?owner_id={owner_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["images"]) == 2
    finally:
        app.dependency_overrides.clear()


def test_delete_image_success(client):
    """Test successful image deletion."""
    image_id = uuid.uuid4()
    mock_service = MagicMock()
    mock_service.delete_image = AsyncMock(return_value=True)

    mock_session = AsyncMock()

    app.dependency_overrides[get_image_service] = lambda: mock_service
    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        response = client.delete(f"/api/v1/images/{image_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True
    finally:
        app.dependency_overrides.clear()


def test_delete_image_not_found(client):
    """Test 404 when deleting non-existent image."""
    mock_service = MagicMock()
    mock_service.delete_image = AsyncMock(return_value=False)

    mock_session = AsyncMock()

    app.dependency_overrides[get_image_service] = lambda: mock_service
    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        response = client.delete(f"/api/v1/images/{uuid.uuid4()}")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
