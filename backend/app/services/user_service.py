"""User service for CRUD operations."""

import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.models.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """Service for user CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_user(self, data: UserCreate) -> User:
        """Create a new user.

        Args:
            data: User creation data.

        Returns:
            The created User ORM instance.

        Raises:
            IntegrityError: If a user with the same email already exists.
        """
        user = User(
            id=uuid.uuid4(),
            email=data.email,
            display_name=data.display_name,
        )
        self._session.add(user)
        try:
            await self._session.flush()
        except IntegrityError:
            await self._session.rollback()
            logger.warning(
                "Duplicate user email",
                extra={"user_email": data.email},
            )
            raise
        await self._session.commit()
        await self._session.refresh(user)
        logger.info(
            "User created",
            extra={"user_id": str(user.id), "user_email": user.email},
        )
        return user

    async def get_user(self, user_id: uuid.UUID) -> User | None:
        """Fetch a user by ID.

        Args:
            user_id: The UUID of the user.

        Returns:
            The User ORM instance or None if not found.
        """
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Fetch a user by email.

        Args:
            email: The user email address.

        Returns:
            The User ORM instance or None if not found.
        """
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_users(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[User], int]:
        """List users with pagination.

        Args:
            limit: Maximum number of users to return.
            offset: Number of users to skip.

        Returns:
            Tuple of (list of User ORM instances, total count).
        """
        count_result = await self._session.execute(select(func.count()).select_from(User))
        total = count_result.scalar_one()

        result = await self._session.execute(
            select(User).order_by(User.display_name).limit(limit).offset(offset)
        )
        users = list(result.scalars().all())

        logger.info(
            "Listed users",
            extra={
                "total": total,
                "returned": len(users),
                "limit": limit,
                "offset": offset,
            },
        )
        return users, total

    async def update_user(self, user_id: uuid.UUID, data: UserUpdate) -> User | None:
        """Partially update a user.

        Args:
            user_id: The UUID of the user.
            data: Fields to update.

        Returns:
            The updated User ORM instance, or None if not found.

        Raises:
            IntegrityError: If the updated email conflicts with an existing user.
        """
        user = await self.get_user(user_id)
        if user is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return user

        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            await self._session.flush()
        except IntegrityError:
            await self._session.rollback()
            logger.warning(
                "User update caused duplicate email",
                extra={"user_id": str(user_id), "data": update_data},
            )
            raise
        await self._session.commit()
        await self._session.refresh(user)
        logger.info(
            "User updated",
            extra={"user_id": str(user_id), "fields": list(update_data)},
        )
        return user

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete a user by ID.

        Args:
            user_id: The UUID of the user.

        Returns:
            True if the user was deleted, False if not found.
        """
        user = await self.get_user(user_id)
        if user is None:
            return False

        await self._session.delete(user)
        await self._session.commit()
        logger.info("User deleted", extra={"user_id": str(user_id)})
        return True
