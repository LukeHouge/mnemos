"""Unit tests for image service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.image_service import (
    ALLOWED_MIME_TYPES,
    MAX_IMAGE_SIZE_BYTES,
    ImageService,
)


@pytest.fixture
def image_service():
    """Create a fresh ImageService instance."""
    return ImageService()


@pytest.fixture
def mock_session():
    """Create a mock async database session."""
    return AsyncMock()


@pytest.fixture
def sample_image_data():
    """Return minimal valid image bytes."""
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


@pytest.fixture
def owner_id():
    """Return a fixed owner UUID."""
    return uuid.uuid4()


@pytest.mark.asyncio
async def test_upload_image_success(image_service, mock_session, sample_image_data, owner_id):
    """Test successful image upload."""
    mock_image = MagicMock()
    mock_image.id = uuid.uuid4()
    mock_image.filename = "photo.png"
    mock_image.mime_type = "image/png"
    mock_image.file_size_bytes = len(sample_image_data)

    with patch("app.services.image_service.Image", return_value=mock_image):
        result = await image_service.upload_image(
            session=mock_session,
            filename="photo.png",
            mime_type="image/png",
            image_data=sample_image_data,
            owner_id=owner_id,
        )

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()
    assert result is mock_image


@pytest.mark.asyncio
async def test_upload_image_invalid_mime_type(
    image_service, mock_session, sample_image_data, owner_id
):
    """Test upload rejects unsupported MIME types."""
    with pytest.raises(ValueError, match="Unsupported image type"):
        await image_service.upload_image(
            session=mock_session,
            filename="file.txt",
            mime_type="text/plain",
            image_data=sample_image_data,
            owner_id=owner_id,
        )


@pytest.mark.asyncio
async def test_upload_image_too_large(image_service, mock_session, owner_id):
    """Test upload rejects images exceeding size limit."""
    big_data = b"\x00" * (MAX_IMAGE_SIZE_BYTES + 1)
    with pytest.raises(ValueError, match="exceeds maximum size"):
        await image_service.upload_image(
            session=mock_session,
            filename="huge.png",
            mime_type="image/png",
            image_data=big_data,
            owner_id=owner_id,
        )


@pytest.mark.asyncio
async def test_upload_image_empty_data(image_service, mock_session, owner_id):
    """Test upload rejects empty image data."""
    with pytest.raises(ValueError, match="empty"):
        await image_service.upload_image(
            session=mock_session,
            filename="empty.png",
            mime_type="image/png",
            image_data=b"",
            owner_id=owner_id,
        )


@pytest.mark.asyncio
async def test_get_image_found(image_service, mock_session):
    """Test retrieving an existing image."""
    mock_image = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_image
    mock_session.execute.return_value = mock_result

    result = await image_service.get_image(mock_session, uuid.uuid4())
    assert result is mock_image


@pytest.mark.asyncio
async def test_get_image_not_found(image_service, mock_session):
    """Test retrieving a non-existent image returns None."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await image_service.get_image(mock_session, uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_delete_image_success(image_service, mock_session):
    """Test successful image deletion."""
    mock_image = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_image
    mock_session.execute.return_value = mock_result

    result = await image_service.delete_image(mock_session, uuid.uuid4())
    assert result is True
    mock_session.delete.assert_awaited_once_with(mock_image)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_image_not_found(image_service, mock_session):
    """Test deleting a non-existent image returns False."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await image_service.delete_image(mock_session, uuid.uuid4())
    assert result is False


def test_allowed_mime_types_contains_common_formats():
    """Test that common image formats are in the allowed list."""
    assert "image/jpeg" in ALLOWED_MIME_TYPES
    assert "image/png" in ALLOWED_MIME_TYPES
    assert "image/webp" in ALLOWED_MIME_TYPES
