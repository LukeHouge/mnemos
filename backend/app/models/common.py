"""Common models used across the application."""

from enum import StrEnum, auto

from pydantic import BaseModel, Field


class ServiceStatusEnum(StrEnum):
    """Service availability status values."""

    AVAILABLE = auto()
    UNAVAILABLE = auto()
    ERROR = auto()


class ServiceStatus(BaseModel):
    """Generic service availability status."""

    status: ServiceStatusEnum = Field(..., description="Service status")
    message: str = Field(..., description="Human-readable status message")
