"""OpenAI service for handling AI operations."""

import logging

from openai import AsyncOpenAI, OpenAIError

from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for OpenAI API operations."""

    def __init__(self):
        """Initialize OpenAI client if API key is available."""
        self._client: AsyncOpenAI | None = None
        if settings.OPENAI_API_KEY:
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            logger.warning("OpenAI API key not configured")

    @property
    def is_available(self) -> bool:
        """Check if OpenAI service is available."""
        return self._client is not None

    async def chat_completion(
        self,
        message: str,
        model: str = "gpt-4o-mini",
        system_prompt: str = "You are a helpful assistant for the Mnemos document management system.",
        max_tokens: int = 500,
    ) -> tuple[str | None, str, int]:
        """
        Send a chat completion request to OpenAI.

        Args:
            message: User message
            model: OpenAI model to use
            system_prompt: System prompt for context
            max_tokens: Maximum tokens in response

        Returns:
            Tuple of (response_text, model_used, tokens_used)
            Returns (None, model, 0) if service unavailable or error occurs

        Raises:
            ValueError: If service is not available
        """
        if not self.is_available:
            error_msg = "AI service not available"
            logger.error("Attempted to use OpenAI service without API key")
            raise ValueError(error_msg)

        # TODO: testing 2
        try:
            response = await self._client.chat.completions.create(  # type: ignore[union-attr]
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                max_tokens=max_tokens,
            )
        except OpenAIError as e:
            logger.error(
                f"OpenAI API error: {type(e).__name__} - {str(e)[:100]}",
                extra={"error": str(e), "model": model},
                exc_info=True,
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in chat completion: {type(e).__name__}",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise
        else:
            content = response.choices[0].message.content or ""
            tokens = response.usage.total_tokens if response.usage else 0

            logger.info(
                f"Chat completion successful - model: {response.model}, tokens: {tokens}",
                extra={
                    "model": response.model,
                    "tokens": tokens,
                    "message_length": len(message),
                },
            )

            return content, response.model, tokens

    async def test_connection(self) -> tuple[bool, str]:
        """
        Test OpenAI API connection.

        Returns:
            Tuple of (success, message)
        """
        if not self.is_available:
            return False, "Service not configured"

        try:
            await self._client.models.list()  # type: ignore[union-attr]
        except OpenAIError as e:
            logger.error(f"❌ OpenAI connection test failed: {type(e).__name__}", exc_info=True)
            return False, f"Connection failed: {type(e).__name__}"
        except Exception as e:
            logger.error(
                f"❌ Unexpected error testing OpenAI connection: {type(e).__name__}", exc_info=True
            )
            return False, f"Unexpected error: {type(e).__name__}"
        else:
            logger.info("✅ OpenAI connection test successful")
            return True, "Connected successfully"


# Singleton instance
_openai_service: OpenAIService | None = None


def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service instance."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
