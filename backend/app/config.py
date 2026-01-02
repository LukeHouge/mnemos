from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # No env_file specified - Docker Compose loads environment files
        # and passes them as environment variables
        case_sensitive=True,
    )

    APP_NAME: str = "Mnemos"
    DEBUG: bool = False
    OPENAI_API_KEY: str | None = None  # Optional - for OpenAI features
    CORS_ORIGINS: str = "*"  # Comma-separated origins, or "*" for all

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS into a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
