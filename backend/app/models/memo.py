"""Memo/note request and response models."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class MemoCreate(BaseModel):
    """Request model for creating a memo."""

    title: str | None = Field(None, max_length=500, description="Optional short title for the memo")
    content: str = Field(..., min_length=1, description="The memo/note content")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")


class MemoUpdate(BaseModel):
    """Request model for updating a memo. All fields optional."""

    title: str | None = Field(None, max_length=500, description="Updated title")
    content: str | None = Field(None, min_length=1, description="Updated content")
    tags: list[str] | None = Field(None, description="Updated tags")


class MemoResponse(BaseModel):
    """Response model for a single memo."""

    id: uuid.UUID = Field(..., description="Memo unique identifier")
    title: str | None = Field(None, description="Memo title")
    content: str = Field(..., description="Memo content")
    tags: list[str] = Field(default_factory=list, description="Memo tags")
    created_at: datetime = Field(..., description="When the memo was created")
    updated_at: datetime = Field(..., description="When the memo was last updated")


class MemoListResponse(BaseModel):
    """Response model for listing memos."""

    memos: list[MemoResponse] = Field(..., description="List of memos")
    total: int = Field(..., ge=0, description="Total number of memos matching the query")
