"""Unit tests for MemoService (mocked database session)."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.models import Memo
from app.models.memo import MemoCreate, MemoUpdate
from app.services.memo_service import MemoService


def _make_memo(
    memo_id: uuid.UUID | None = None,
    title: str | None = "Test",
    content: str = "Hello",
    tags: list[str] | None = None,
) -> Memo:
    """Build a Memo ORM instance for testing."""
    now = datetime.now(tz=timezone.utc)
    return Memo(
        id=memo_id or uuid.uuid4(),
        title=title,
        content=content,
        tags=tags or [],
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def session():
    """Provide a mock async database session."""
    mock = AsyncMock()
    mock.add = MagicMock()
    return mock


@pytest.fixture
def service(session):
    """Provide a MemoService backed by the mock session."""
    return MemoService(session)


class TestCreateMemo:
    """Tests for MemoService.create_memo."""

    @pytest.mark.asyncio
    async def test_create_adds_and_commits(self, service, session):
        """create_memo adds memo, commits, and refreshes."""
        memo_obj = _make_memo()

        async def fake_refresh(obj: Memo) -> None:
            obj.id = memo_obj.id
            obj.created_at = memo_obj.created_at
            obj.updated_at = memo_obj.updated_at

        session.refresh = AsyncMock(side_effect=fake_refresh)

        result = await service.create_memo(MemoCreate(content="Hello", tags=["a"]))

        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once()


class TestGetMemo:
    """Tests for MemoService.get_memo."""

    @pytest.mark.asyncio
    async def test_get_returns_memo(self, service, session):
        """get_memo returns MemoResponse when memo exists."""
        memo = _make_memo()
        session.get = AsyncMock(return_value=memo)

        result = await service.get_memo(memo.id)

        assert result is not None
        assert result.id == memo.id
        assert result.content == memo.content

    @pytest.mark.asyncio
    async def test_get_returns_none_when_missing(self, service, session):
        """get_memo returns None when memo does not exist."""
        session.get = AsyncMock(return_value=None)

        result = await service.get_memo(uuid.uuid4())

        assert result is None


class TestUpdateMemo:
    """Tests for MemoService.update_memo."""

    @pytest.mark.asyncio
    async def test_update_applies_changes(self, service, session):
        """update_memo modifies existing memo fields."""
        memo = _make_memo(content="Old")
        session.get = AsyncMock(return_value=memo)
        session.refresh = AsyncMock()

        result = await service.update_memo(
            memo.id, MemoUpdate(content="New")
        )

        assert memo.content == "New"
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_returns_none_when_missing(self, service, session):
        """update_memo returns None when memo does not exist."""
        session.get = AsyncMock(return_value=None)

        result = await service.update_memo(uuid.uuid4(), MemoUpdate(content="X"))

        assert result is None
        session.commit.assert_not_awaited()


class TestDeleteMemo:
    """Tests for MemoService.delete_memo."""

    @pytest.mark.asyncio
    async def test_delete_returns_true(self, service, session):
        """delete_memo returns True when memo is deleted."""
        memo = _make_memo()
        session.get = AsyncMock(return_value=memo)

        result = await service.delete_memo(memo.id)

        assert result is True
        session.delete.assert_awaited_once_with(memo)
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_returns_false_when_missing(self, service, session):
        """delete_memo returns False when memo does not exist."""
        session.get = AsyncMock(return_value=None)

        result = await service.delete_memo(uuid.uuid4())

        assert result is False
        session.delete.assert_not_awaited()
