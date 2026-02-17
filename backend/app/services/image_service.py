"""Image storage service for managing uploaded images."""

import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Image

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
    }
)

MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class ImageService:
    """Service for image CRUD operations."""

    async def upload_image(  # noqa: PLR0913
        self,
        session: AsyncSession,
        filename: str,
        mime_type: str,
        image_data: bytes,
        owner_id: uuid.UUID,
        description: str | None = None,
    ) -> Image:
        """Store an uploaded image in the database.

        Args:
            session: Database session.
            filename: Original filename.
            mime_type: MIME type of the image.
            image_data: Raw image bytes.
            owner_id: UUID of the owning user.
            description: Optional description.

        Returns:
            The created Image ORM instance.

        Raises:
            ValueError: If mime_type or file size is invalid.
        """
        if mime_type not in ALLOWED_MIME_TYPES:
            msg = f"Unsupported image type: {mime_type}"
            raise ValueError(msg)

        file_size = len(image_data)
        if file_size > MAX_IMAGE_SIZE_BYTES:
            msg = f"Image exceeds maximum size of {MAX_IMAGE_SIZE_BYTES} bytes"
            raise ValueError(msg)

        if file_size == 0:
            msg = "Image data is empty"
            raise ValueError(msg)

        image = Image(
            filename=filename,
            description=description,
            mime_type=mime_type,
            file_size_bytes=file_size,
            image_data=image_data,
            owner_id=owner_id,
        )
        session.add(image)
        await session.commit()
        await session.refresh(image)

        logger.info(
            f"Image uploaded: {image.id}",
            extra={"image_id": str(image.id), "image_filename": filename, "size": file_size},
        )
        return image

    async def get_image(self, session: AsyncSession, image_id: uuid.UUID) -> Image | None:
        """Retrieve a single image by ID.

        Args:
            session: Database session.
            image_id: UUID of the image.

        Returns:
            The Image instance, or None if not found.
        """
        result = await session.execute(select(Image).where(Image.id == image_id))
        return result.scalar_one_or_none()

    async def list_images(
        self,
        session: AsyncSession,
        owner_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Image], int]:
        """List images for a given owner.

        Args:
            session: Database session.
            owner_id: UUID of the owning user.
            limit: Max number of images to return.
            offset: Number of images to skip.

        Returns:
            Tuple of (list of images, total count).
        """
        count_result = await session.execute(
            select(func.count()).select_from(Image).where(Image.owner_id == owner_id)
        )
        total = count_result.scalar_one()

        result = await session.execute(
            select(Image)
            .where(Image.owner_id == owner_id)
            .order_by(Image.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        images = list(result.scalars().all())

        return images, total

    async def delete_image(self, session: AsyncSession, image_id: uuid.UUID) -> bool:
        """Delete an image by ID.

        Args:
            session: Database session.
            image_id: UUID of the image to delete.

        Returns:
            True if deleted, False if not found.
        """
        image = await self.get_image(session, image_id)
        if image is None:
            return False

        await session.delete(image)
        await session.commit()

        logger.info(f"Image deleted: {image_id}", extra={"image_id": str(image_id)})
        return True


# Singleton instance
_image_service: ImageService | None = None


def get_image_service() -> ImageService:
    """Get or create ImageService instance."""
    global _image_service
    if _image_service is None:
        _image_service = ImageService()
    return _image_service
