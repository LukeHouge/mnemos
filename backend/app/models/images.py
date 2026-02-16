"""Image storage request/response models."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ImageMetadataResponse(BaseModel):
    """Response model for image metadata (without binary data)."""

    id: uuid.UUID = Field(..., description="Image unique identifier")
    filename: str = Field(..., description="Original filename")
    description: str | None = Field(None, description="Image description")
    mime_type: str = Field(..., description="MIME type of the image")
    file_size_bytes: int = Field(..., ge=0, description="File size in bytes")
    extracted_text: str | None = Field(None, description="OCR-extracted text")
    owner_id: uuid.UUID = Field(..., description="Owner user ID")
    created_at: datetime = Field(..., description="Upload timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ImageListResponse(BaseModel):
    """Response model for listing images."""

    images: list[ImageMetadataResponse] = Field(..., description="List of image metadata")
    total: int = Field(..., ge=0, description="Total number of images")


class ImageUploadResponse(BaseModel):
    """Response model after successful image upload."""

    id: uuid.UUID = Field(..., description="Newly created image ID")
    filename: str = Field(..., description="Stored filename")
    mime_type: str = Field(..., description="Detected MIME type")
    file_size_bytes: int = Field(..., ge=0, description="File size in bytes")


class ImageDeleteResponse(BaseModel):
    """Response model after successful image deletion."""

    deleted: bool = Field(..., description="Whether the image was deleted")
    id: uuid.UUID = Field(..., description="Deleted image ID")
