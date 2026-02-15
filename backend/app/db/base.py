"""SQLAlchemy async engine and session factory."""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for dependency injection."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_db_connection() -> tuple[bool, str]:
    """
    Test database connectivity.

    Returns:
        Tuple of (success, message)
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(
            f"Database connection check failed: {type(e).__name__}",
            exc_info=True,
        )
        return False, f"Connection failed: {type(e).__name__}"
    else:
        return True, "Connected successfully"


async def dispose_engine() -> None:
    """Dispose of the database engine and close all connections."""
    await engine.dispose()
    logger.info("Database engine disposed")
