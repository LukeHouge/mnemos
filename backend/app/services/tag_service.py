"""Tag service for CRUD operations."""

import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Tag
from app.models.tag import TagCreate, TagUpdate

logger = logging.getLogger(__name__)


class TagService:
    """Service for tag CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_tag(self, data: TagCreate) -> Tag:
        """Create a new tag.

        Args:
            data: Tag creation data.

        Returns:
            The created Tag ORM instance.

        Raises:
            IntegrityError: If a tag with the same name already exists.
        """
        tag = Tag(
            id=uuid.uuid4(),
            name=data.name,
            color=data.color,
        )
        self._session.add(tag)
        try:
            await self._session.flush()
        except IntegrityError:
            await self._session.rollback()
            logger.warning("Duplicate tag name", extra={"tag_name": data.name})
            raise
        await self._session.commit()
        await self._session.refresh(tag)
        logger.info("Tag created", extra={"tag_id": str(tag.id), "tag_name": tag.name})
        return tag

    async def get_tag(self, tag_id: uuid.UUID) -> Tag | None:
        """Fetch a tag by ID.

        Args:
            tag_id: The UUID of the tag.

        Returns:
            The Tag ORM instance or None if not found.
        """
        result = await self._session.execute(select(Tag).where(Tag.id == tag_id))
        return result.scalar_one_or_none()

    async def get_tag_by_name(self, name: str) -> Tag | None:
        """Fetch a tag by name.

        Args:
            name: The tag name.

        Returns:
            The Tag ORM instance or None if not found.
        """
        result = await self._session.execute(select(Tag).where(Tag.name == name))
        return result.scalar_one_or_none()

    async def list_tags(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Tag], int]:
        """List tags with pagination.

        Args:
            limit: Maximum number of tags to return.
            offset: Number of tags to skip.

        Returns:
            Tuple of (list of Tag ORM instances, total count).
        """
        count_result = await self._session.execute(select(func.count()).select_from(Tag))
        total = count_result.scalar_one()

        result = await self._session.execute(
            select(Tag).order_by(Tag.name).limit(limit).offset(offset)
        )
        tags = list(result.scalars().all())

        logger.info(
            "Listed tags",
            extra={"total": total, "returned": len(tags), "limit": limit, "offset": offset},
        )
        return tags, total

    async def update_tag(self, tag_id: uuid.UUID, data: TagUpdate) -> Tag | None:
        """Partially update a tag.

        Args:
            tag_id: The UUID of the tag.
            data: Fields to update.

        Returns:
            The updated Tag ORM instance, or None if not found.

        Raises:
            IntegrityError: If the updated name conflicts with an existing tag.
        """
        tag = await self.get_tag(tag_id)
        if tag is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return tag

        for field, value in update_data.items():
            setattr(tag, field, value)

        try:
            await self._session.flush()
        except IntegrityError:
            await self._session.rollback()
            logger.warning(
                "Tag update caused duplicate name",
                extra={"tag_id": str(tag_id), "data": update_data},
            )
            raise
        await self._session.commit()
        await self._session.refresh(tag)
        logger.info("Tag updated", extra={"tag_id": str(tag_id), "fields": list(update_data)})
        return tag

    async def delete_tag(self, tag_id: uuid.UUID) -> bool:
        """Delete a tag by ID.

        Args:
            tag_id: The UUID of the tag.

        Returns:
            True if the tag was deleted, False if not found.
        """
        tag = await self.get_tag(tag_id)
        if tag is None:
            return False

        await self._session.delete(tag)
        await self._session.commit()
        logger.info("Tag deleted", extra={"tag_id": str(tag_id)})
        return True
