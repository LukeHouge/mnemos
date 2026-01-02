"""Error response models."""

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail for validation errors."""

    field: str | None = Field(None, description="Field name (if validation error)")
    message: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")
    request_id: str | None = Field(None, description="Request ID for tracing")
    errors: list[ErrorDetail] | None = Field(None, description="Validation errors (if applicable)")
