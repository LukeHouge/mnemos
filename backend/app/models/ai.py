"""AI service request/response models."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., min_length=1, description="User message to send to AI")
    model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use",
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(..., description="AI-generated response")
    model: str = Field(..., description="Model that generated the response")
    tokens_used: int = Field(..., ge=0, description="Total tokens used")
