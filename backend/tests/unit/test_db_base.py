"""Unit tests for database base module (engine, session, connection check)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.base import check_db_connection, dispose_engine, get_session


@patch("app.db.base.engine")
async def test_check_db_connection_success(mock_engine):
    """Test successful database connection check."""
    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock()
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_context.__aexit__ = AsyncMock(return_value=False)
    mock_engine.connect.return_value = mock_context

    success, message = await check_db_connection()

    assert success is True
    assert "successfully" in message.lower()


@patch("app.db.base.engine")
async def test_check_db_connection_failure(mock_engine):
    """Test database connection check when database is unreachable."""
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(side_effect=ConnectionRefusedError("Connection refused"))
    mock_context.__aexit__ = AsyncMock(return_value=False)
    mock_engine.connect.return_value = mock_context

    success, message = await check_db_connection()

    assert success is False
    assert "ConnectionRefusedError" in message


@patch("app.db.base.engine")
async def test_dispose_engine(mock_engine):
    """Test engine disposal."""
    mock_engine.dispose = AsyncMock()

    await dispose_engine()

    mock_engine.dispose.assert_awaited_once()


@patch("app.db.base.async_session_factory")
async def test_get_session_yields_session(mock_factory):
    """Test that get_session yields a database session."""
    mock_session = AsyncMock()
    mock_context = MagicMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_session)
    mock_context.__aexit__ = AsyncMock(return_value=False)
    mock_factory.return_value = mock_context

    async for session in get_session():
        assert session is mock_session
