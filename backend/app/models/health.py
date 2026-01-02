"""Health check models."""

from enum import StrEnum, auto

from pydantic import BaseModel, Field


class OverallHealthStatusEnum(StrEnum):
    """Overall health status values."""

    HEALTHY = auto()
    DEGRADED = auto()


class ServiceHealthStatusEnum(StrEnum):
    """Individual service health status values."""

    CONNECTED = auto()
    ERROR = auto()
    NOT_CONFIGURED = auto()


class HealthCheck(BaseModel):
    """Basic health check response."""

    status: OverallHealthStatusEnum = Field(..., description="Health status")
    version: str = Field(..., description="API version")


class ServiceHealthStatus(BaseModel):
    """Individual service health status."""

    status: ServiceHealthStatusEnum = Field(..., description="Service status")
    message: str = Field(..., description="Status message")


class DetailedHealthCheck(BaseModel):
    """Detailed health check with all service statuses."""

    status: OverallHealthStatusEnum = Field(..., description="Overall health status")
    version: str = Field(..., description="API version")
    services: dict[str, ServiceHealthStatus] = Field(
        ...,
        description="Status of all external services",
    )
