"""Unit tests for UserService with mocked database session."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import UserCreate, UserUpdate
from app.services.user_service import UserService


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock async SQLAlchemy session."""
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def user_service(mock_session: AsyncMock) -> UserService:
    """Create a UserService with a mocked session."""
    return UserService(mock_session)


def _make_mock_user(
    user_id: uuid.UUID | None = None,
    email: str = "alice@example.com",
    display_name: str = "Alice",
) -> MagicMock:
    """Build a mock User ORM object."""
    user = MagicMock()
    user.id = user_id or uuid.uuid4()
    user.email = email
    user.display_name = display_name
    user.created_at = datetime.now(tz=timezone.utc)
    user.updated_at = datetime.now(tz=timezone.utc)
    return user


class TestCreateUser:
    """Tests for UserService.create_user."""

    @pytest.mark.asyncio
    async def test_create_user_success(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """create_user inserts a user and commits."""
        data = UserCreate(email="alice@example.com", display_name="Alice")
        user = await user_service.create_user(data)

        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()
        added_obj = mock_session.add.call_args[0][0]
        assert added_obj.email == "alice@example.com"
        assert added_obj.display_name == "Alice"

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email_raises(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """create_user raises IntegrityError on duplicate email."""
        mock_session.flush.side_effect = IntegrityError(
            "duplicate", params=None, orig=Exception()
        )
        data = UserCreate(email="duplicate@example.com", display_name="Dup")

        with pytest.raises(IntegrityError):
            await user_service.create_user(data)

        mock_session.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_user_assigns_uuid(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """create_user assigns a UUID to the new user."""
        data = UserCreate(email="bob@example.com", display_name="Bob")
        await user_service.create_user(data)

        added_obj = mock_session.add.call_args[0][0]
        assert added_obj.id is not None


class TestGetUser:
    """Tests for UserService.get_user."""

    @pytest.mark.asyncio
    async def test_get_user_found(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """get_user returns the user when found."""
        user_id = uuid.uuid4()
        mock_user = _make_mock_user(user_id=user_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        result = await user_service.get_user(user_id)

        assert result is mock_user

    @pytest.mark.asyncio
    async def test_get_user_not_found(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """get_user returns None when the user does not exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await user_service.get_user(uuid.uuid4())

        assert result is None


class TestGetUserByEmail:
    """Tests for UserService.get_user_by_email."""

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """get_user_by_email returns the user when found."""
        mock_user = _make_mock_user(email="alice@example.com")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        result = await user_service.get_user_by_email("alice@example.com")

        assert result is mock_user

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """get_user_by_email returns None when the user does not exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await user_service.get_user_by_email("nobody@example.com")

        assert result is None


class TestListUsers:
    """Tests for UserService.list_users."""

    @pytest.mark.asyncio
    async def test_list_users_returns_items_and_total(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """list_users returns a list of users and the total count."""
        mock_users = [
            _make_mock_user(email="alice@example.com"),
            _make_mock_user(email="bob@example.com"),
        ]

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = mock_users
        list_result = MagicMock()
        list_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, list_result]

        users, total = await user_service.list_users(limit=20, offset=0)

        assert len(users) == 2
        assert total == 2

    @pytest.mark.asyncio
    async def test_list_users_empty(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """list_users returns empty list and zero total when no users exist."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        list_result = MagicMock()
        list_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, list_result]

        users, total = await user_service.list_users()

        assert users == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_list_users_respects_pagination(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """list_users passes limit and offset to the query."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 5

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [_make_mock_user()]
        list_result = MagicMock()
        list_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, list_result]

        users, total = await user_service.list_users(limit=1, offset=3)

        assert len(users) == 1
        assert total == 5


class TestUpdateUser:
    """Tests for UserService.update_user."""

    @pytest.mark.asyncio
    async def test_update_user_success(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """update_user modifies the user and commits."""
        user_id = uuid.uuid4()
        mock_user = _make_mock_user(user_id=user_id, display_name="Old Name")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        data = UserUpdate(display_name="New Name")
        result = await user_service.update_user(user_id, data)

        assert result is mock_user
        mock_session.flush.assert_awaited_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_user_not_found(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """update_user returns None when the user does not exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await user_service.update_user(
            uuid.uuid4(), UserUpdate(display_name="New")
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_update_user_no_fields(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """update_user with no fields returns the user unchanged."""
        user_id = uuid.uuid4()
        mock_user = _make_mock_user(user_id=user_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        result = await user_service.update_user(user_id, UserUpdate())

        assert result is mock_user
        mock_session.flush.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_user_duplicate_email_raises(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """update_user raises IntegrityError on duplicate email."""
        user_id = uuid.uuid4()
        mock_user = _make_mock_user(user_id=user_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        mock_session.flush.side_effect = IntegrityError(
            "duplicate", params=None, orig=Exception()
        )

        with pytest.raises(IntegrityError):
            await user_service.update_user(
                user_id, UserUpdate(email="taken@example.com")
            )

        mock_session.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_user_email_only(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """update_user can update just the email."""
        user_id = uuid.uuid4()
        mock_user = _make_mock_user(user_id=user_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        data = UserUpdate(email="new@example.com")
        result = await user_service.update_user(user_id, data)

        assert result is mock_user
        mock_session.flush.assert_awaited_once()
        mock_session.commit.assert_awaited_once()


class TestDeleteUser:
    """Tests for UserService.delete_user."""

    @pytest.mark.asyncio
    async def test_delete_user_success(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """delete_user removes the user and returns True."""
        user_id = uuid.uuid4()
        mock_user = _make_mock_user(user_id=user_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        result = await user_service.delete_user(user_id)

        assert result is True
        mock_session.delete.assert_awaited_once_with(mock_user)
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_user_not_found(
        self, user_service: UserService, mock_session: AsyncMock
    ) -> None:
        """delete_user returns False when the user does not exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await user_service.delete_user(uuid.uuid4())

        assert result is False
