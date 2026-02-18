"""Pydantic schemas for User CRUD operations."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Request model for creating a user."""

    email: EmailStr = Field(
        ...,
        description="User email address (unique)",
    )
    display_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User display name",
    )

    @field_validator("display_name")
    @classmethod
    def display_name_must_not_be_blank(cls, v: str) -> str:
        """Ensure display_name is not just whitespace."""
        stripped = v.strip()
        if not stripped:
            msg = "Display name must not be blank"
            raise ValueError(msg)
        return stripped


class UserUpdate(BaseModel):
    """Request model for updating a user (all fields optional)."""

    email: EmailStr | None = Field(
        None,
        description="User email address (unique)",
    )
    display_name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="User display name",
    )

    @field_validator("display_name")
    @classmethod
    def display_name_must_not_be_blank(cls, v: str | None) -> str | None:
        """Ensure display_name is not just whitespace."""
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            msg = "Display name must not be blank"
            raise ValueError(msg)
        return stripped


class UserResponse(BaseModel):
    """Response model for a single user."""

    id: uuid.UUID = Field(..., description="User unique identifier")
    email: str = Field(..., description="User email address")
    display_name: str = Field(..., description="User display name")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Response model for a paginated list of users."""

    items: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    limit: int = Field(..., description="Page size")
    offset: int = Field(..., description="Page offset")
