"""Pydantic models for document management."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    """Request model for creating a document."""

    title: str = Field(..., min_length=1, max_length=500, description="Document title")
    description: str | None = Field(None, description="Optional document description")
    filename: str = Field(..., min_length=1, max_length=500, description="Original filename")
    file_path: str = Field(..., min_length=1, max_length=1000, description="Storage path")
    file_size_bytes: int = Field(..., gt=0, description="File size in bytes")
    mime_type: str = Field(
        ..., min_length=1, max_length=100, description="MIME type (e.g., application/pdf)"
    )
    owner_id: uuid.UUID = Field(..., description="ID of the user who owns this document")


class DocumentUpdate(BaseModel):
    """Request model for updating a document (all fields optional)."""

    title: str | None = Field(None, min_length=1, max_length=500, description="Document title")
    description: str | None = Field(None, description="Document description")
    filename: str | None = Field(
        None, min_length=1, max_length=500, description="Original filename"
    )
    file_path: str | None = Field(None, min_length=1, max_length=1000, description="Storage path")
    file_size_bytes: int | None = Field(None, gt=0, description="File size in bytes")
    mime_type: str | None = Field(
        None, min_length=1, max_length=100, description="MIME type (e.g., application/pdf)"
    )


class TagResponse(BaseModel):
    """Response model for a tag associated with a document."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Tag ID")
    name: str = Field(..., description="Tag name")
    color: str | None = Field(None, description="Tag color hex code")


class DocumentResponse(BaseModel):
    """Response model for a document."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    description: str | None = Field(None, description="Document description")
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="Storage path")
    file_size_bytes: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    owner_id: uuid.UUID = Field(..., description="Owner user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    tags: list[TagResponse] = Field(default_factory=list, description="Associated tags")


class DocumentListResponse(BaseModel):
    """Paginated list of documents."""

    documents: list[DocumentResponse] = Field(..., description="List of documents")
    total: int = Field(..., ge=0, description="Total number of documents matching filters")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
