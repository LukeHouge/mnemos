"""Unit tests for image Pydantic models."""

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.images import (
    ImageDeleteResponse,
    ImageListResponse,
    ImageMetadataResponse,
    ImageUploadResponse,
)


def test_image_metadata_response_valid():
    """Test ImageMetadataResponse with valid data."""
    now = datetime.now(tz=UTC)
    resp = ImageMetadataResponse(
        id=uuid.uuid4(),
        filename="photo.jpg",
        description="A test photo",
        mime_type="image/jpeg",
        file_size_bytes=1024,
        extracted_text=None,
        owner_id=uuid.uuid4(),
        created_at=now,
        updated_at=now,
    )
    assert resp.filename == "photo.jpg"
    assert resp.file_size_bytes == 1024


def test_image_metadata_response_negative_size():
    """Test ImageMetadataResponse rejects negative file size."""
    now = datetime.now(tz=UTC)
    with pytest.raises(ValidationError):
        ImageMetadataResponse(
            id=uuid.uuid4(),
            filename="photo.jpg",
            mime_type="image/jpeg",
            file_size_bytes=-1,
            owner_id=uuid.uuid4(),
            created_at=now,
            updated_at=now,
        )


def test_image_upload_response_valid():
    """Test ImageUploadResponse with valid data."""
    resp = ImageUploadResponse(
        id=uuid.uuid4(),
        filename="photo.png",
        mime_type="image/png",
        file_size_bytes=2048,
    )
    assert resp.mime_type == "image/png"


def test_image_delete_response_valid():
    """Test ImageDeleteResponse with valid data."""
    img_id = uuid.uuid4()
    resp = ImageDeleteResponse(deleted=True, id=img_id)
    assert resp.deleted is True
    assert resp.id == img_id


def test_image_list_response_valid():
    """Test ImageListResponse with valid data."""
    resp = ImageListResponse(images=[], total=0)
    assert resp.total == 0
    assert resp.images == []


def test_image_list_response_negative_total():
    """Test ImageListResponse rejects negative total."""
    with pytest.raises(ValidationError):
        ImageListResponse(images=[], total=-1)
