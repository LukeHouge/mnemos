"""Unit tests for TagService with mocked database session."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.tag import TagCreate, TagUpdate
from app.services.tag_service import TagService


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock async SQLAlchemy session."""
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def tag_service(mock_session: AsyncMock) -> TagService:
    """Create a TagService with a mocked session."""
    return TagService(mock_session)


def _make_mock_tag(
    tag_id: uuid.UUID | None = None,
    name: str = "receipts",
    color: str | None = "#FF5733",
) -> MagicMock:
    """Build a mock Tag ORM object."""
    tag = MagicMock()
    tag.id = tag_id or uuid.uuid4()
    tag.name = name
    tag.color = color
    tag.created_at = datetime.now(tz=timezone.utc)
    return tag


class TestCreateTag:
    """Tests for TagService.create_tag."""

    @pytest.mark.asyncio
    async def test_create_tag_success(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """create_tag inserts a tag and commits."""
        data = TagCreate(name="receipts", color="#FF5733")
        tag = await tag_service.create_tag(data)

        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()
        added_obj = mock_session.add.call_args[0][0]
        assert added_obj.name == "receipts"
        assert added_obj.color == "#FF5733"

    @pytest.mark.asyncio
    async def test_create_tag_duplicate_name_raises(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """create_tag raises IntegrityError on duplicate name."""
        mock_session.flush.side_effect = IntegrityError(
            "duplicate", params=None, orig=Exception()
        )
        data = TagCreate(name="duplicate")

        with pytest.raises(IntegrityError):
            await tag_service.create_tag(data)

        mock_session.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_tag_without_color(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """create_tag works without a color field."""
        data = TagCreate(name="manuals")
        await tag_service.create_tag(data)

        added_obj = mock_session.add.call_args[0][0]
        assert added_obj.name == "manuals"
        assert added_obj.color is None


class TestGetTag:
    """Tests for TagService.get_tag."""

    @pytest.mark.asyncio
    async def test_get_tag_found(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """get_tag returns the tag when found."""
        tag_id = uuid.uuid4()
        mock_tag = _make_mock_tag(tag_id=tag_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_tag
        mock_session.execute.return_value = mock_result

        result = await tag_service.get_tag(tag_id)

        assert result is mock_tag

    @pytest.mark.asyncio
    async def test_get_tag_not_found(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """get_tag returns None when the tag does not exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await tag_service.get_tag(uuid.uuid4())

        assert result is None


class TestGetTagByName:
    """Tests for TagService.get_tag_by_name."""

    @pytest.mark.asyncio
    async def test_get_tag_by_name_found(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """get_tag_by_name returns the tag when found."""
        mock_tag = _make_mock_tag(name="invoices")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_tag
        mock_session.execute.return_value = mock_result

        result = await tag_service.get_tag_by_name("invoices")

        assert result is mock_tag

    @pytest.mark.asyncio
    async def test_get_tag_by_name_not_found(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """get_tag_by_name returns None when the tag does not exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await tag_service.get_tag_by_name("nonexistent")

        assert result is None


class TestListTags:
    """Tests for TagService.list_tags."""

    @pytest.mark.asyncio
    async def test_list_tags_returns_items_and_total(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """list_tags returns a list of tags and the total count."""
        mock_tags = [_make_mock_tag(name="a"), _make_mock_tag(name="b")]

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = mock_tags
        list_result = MagicMock()
        list_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, list_result]

        tags, total = await tag_service.list_tags(limit=20, offset=0)

        assert len(tags) == 2
        assert total == 2

    @pytest.mark.asyncio
    async def test_list_tags_empty(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """list_tags returns empty list and zero total when no tags exist."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        list_result = MagicMock()
        list_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, list_result]

        tags, total = await tag_service.list_tags()

        assert tags == []
        assert total == 0


class TestUpdateTag:
    """Tests for TagService.update_tag."""

    @pytest.mark.asyncio
    async def test_update_tag_success(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """update_tag modifies the tag and commits."""
        tag_id = uuid.uuid4()
        mock_tag = _make_mock_tag(tag_id=tag_id, name="old")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_tag
        mock_session.execute.return_value = mock_result

        data = TagUpdate(name="new")
        result = await tag_service.update_tag(tag_id, data)

        assert result is mock_tag
        mock_session.flush.assert_awaited_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_tag_not_found(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """update_tag returns None when the tag does not exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await tag_service.update_tag(uuid.uuid4(), TagUpdate(name="new"))

        assert result is None

    @pytest.mark.asyncio
    async def test_update_tag_no_fields(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """update_tag with no fields returns the tag unchanged."""
        tag_id = uuid.uuid4()
        mock_tag = _make_mock_tag(tag_id=tag_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_tag
        mock_session.execute.return_value = mock_result

        result = await tag_service.update_tag(tag_id, TagUpdate())

        assert result is mock_tag
        mock_session.flush.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_tag_duplicate_name_raises(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """update_tag raises IntegrityError on duplicate name."""
        tag_id = uuid.uuid4()
        mock_tag = _make_mock_tag(tag_id=tag_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_tag
        mock_session.execute.return_value = mock_result

        mock_session.flush.side_effect = IntegrityError(
            "duplicate", params=None, orig=Exception()
        )

        with pytest.raises(IntegrityError):
            await tag_service.update_tag(tag_id, TagUpdate(name="taken"))

        mock_session.rollback.assert_awaited_once()


class TestDeleteTag:
    """Tests for TagService.delete_tag."""

    @pytest.mark.asyncio
    async def test_delete_tag_success(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """delete_tag removes the tag and returns True."""
        tag_id = uuid.uuid4()
        mock_tag = _make_mock_tag(tag_id=tag_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_tag
        mock_session.execute.return_value = mock_result

        result = await tag_service.delete_tag(tag_id)

        assert result is True
        mock_session.delete.assert_awaited_once_with(mock_tag)
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_tag_not_found(
        self, tag_service: TagService, mock_session: AsyncMock
    ) -> None:
        """delete_tag returns False when the tag does not exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await tag_service.delete_tag(uuid.uuid4())

        assert result is False
