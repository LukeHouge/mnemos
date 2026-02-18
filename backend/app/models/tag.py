"""Pydantic schemas for Tag CRUD operations."""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


class TagCreate(BaseModel):
    """Request model for creating a tag."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Tag name (unique)",
    )
    color: str | None = Field(
        None,
        description="Hex color code (#RRGGBB) or null",
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        """Ensure name is not just whitespace."""
        stripped = v.strip()
        if not stripped:
            msg = "Tag name must not be blank"
            raise ValueError(msg)
        return stripped

    @field_validator("color")
    @classmethod
    def color_must_be_hex(cls, v: str | None) -> str | None:
        """Validate hex color format (#RRGGBB)."""
        if v is None:
            return v
        if not HEX_COLOR_PATTERN.match(v):
            msg = "Color must be a valid hex color code (#RRGGBB)"
            raise ValueError(msg)
        return v


class TagUpdate(BaseModel):
    """Request model for updating a tag (all fields optional)."""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Tag name (unique)",
    )
    color: str | None = Field(
        None,
        description="Hex color code (#RRGGBB) or null",
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str | None) -> str | None:
        """Ensure name is not just whitespace."""
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            msg = "Tag name must not be blank"
            raise ValueError(msg)
        return stripped

    @field_validator("color")
    @classmethod
    def color_must_be_hex(cls, v: str | None) -> str | None:
        """Validate hex color format (#RRGGBB)."""
        if v is None:
            return v
        if not HEX_COLOR_PATTERN.match(v):
            msg = "Color must be a valid hex color code (#RRGGBB)"
            raise ValueError(msg)
        return v


class TagResponse(BaseModel):
    """Response model for a single tag."""

    id: uuid.UUID = Field(..., description="Tag unique identifier")
    name: str = Field(..., description="Tag name")
    color: str | None = Field(None, description="Hex color code (#RRGGBB)")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


class TagListResponse(BaseModel):
    """Response model for a paginated list of tags."""

    items: list[TagResponse] = Field(..., description="List of tags")
    total: int = Field(..., description="Total number of tags")
    limit: int = Field(..., description="Page size")
    offset: int = Field(..., description="Page offset")
