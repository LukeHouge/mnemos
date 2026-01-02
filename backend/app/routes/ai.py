import logging

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAIError

from app.models.ai import ChatRequest, ChatResponse
from app.models.common import ServiceStatus, ServiceStatusEnum
from app.services.openai_service import OpenAIService, get_openai_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/ai", tags=["AI"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    openai_service: OpenAIService = Depends(get_openai_service),
) -> ChatResponse:
    """
    Send a chat message to the AI assistant.

    Example request:
    ```json
    {
        "message": "Hello, how are you?",
        "model": "gpt-4o-mini"
    }
    ```
    """
    if not openai_service.is_available:
        logger.warning("Chat request rejected - OpenAI service not available")
        raise HTTPException(
            status_code=503,
            detail="AI service is not available",
        )

    try:
        content, model_used, tokens = await openai_service.chat_completion(
            message=request.message,
            model=request.model,
        )

        if content is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate response",
            )

        return ChatResponse(
            response=content,
            model=model_used,
            tokens_used=tokens,
        )

    except ValueError as e:
        # Service not available
        logger.error("Service error in chat endpoint", exc_info=True)
        raise HTTPException(status_code=503, detail="AI service unavailable") from e
    except OpenAIError as e:
        # OpenAI API error
        logger.error(
            "OpenAI API error in chat endpoint",
            extra={"error_type": type(e).__name__},
            exc_info=True,
        )
        raise HTTPException(
            status_code=502,
            detail="External AI service error",
        ) from e
    except Exception as e:
        # Unexpected error
        logger.error("Unexpected error in chat endpoint", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred",
        ) from e


@router.get("/test", response_model=ServiceStatus)
async def test_openai_connection(
    openai_service: OpenAIService = Depends(get_openai_service),
) -> ServiceStatus:
    """
    Test if AI service is available and functioning.
    """
    if not openai_service.is_available:
        return ServiceStatus(
            status=ServiceStatusEnum.UNAVAILABLE,
            message="AI service not configured",
        )

    success, message = await openai_service.test_connection()

    return ServiceStatus(
        status=ServiceStatusEnum.AVAILABLE if success else ServiceStatusEnum.ERROR,
        message=message,
    )
