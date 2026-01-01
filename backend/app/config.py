from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Mnemos"
    DEBUG: bool = False
    SECRET_KEY: str = Field(...)  # Required - must be set in .env.secrets or environment

    class Config:
        # No env_file specified - Docker Compose loads environment files
        # and passes them as environment variables
        case_sensitive = True


# BaseSettings automatically loads SECRET_KEY from environment at runtime
# Type checkers can't detect this, so we ignore the call-arg error
settings = Settings()  # type: ignore[call-arg]
