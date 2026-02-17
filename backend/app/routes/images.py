"""Image upload, retrieval, and deletion endpoints."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.models.images import (
    ImageDeleteResponse,
    ImageListResponse,
    ImageMetadataResponse,
    ImageUploadResponse,
)
from app.services.image_service import ImageService, get_image_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/images", tags=["Images"])


@router.post("", response_model=ImageUploadResponse, status_code=201)
async def upload_image(
    file: UploadFile,
    owner_id: uuid.UUID,
    description: str | None = None,
    session: AsyncSession = Depends(get_session),
    image_service: ImageService = Depends(get_image_service),
) -> ImageUploadResponse:
    """Upload a new image to the database."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_data = await file.read()
    filename = file.filename or "untitled"

    try:
        image = await image_service.upload_image(
            session=session,
            filename=filename,
            mime_type=file.content_type,
            image_data=image_data,
            owner_id=owner_id,
            description=description,
        )
    except ValueError as e:
        logger.warning(f"Image upload rejected: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e

    return ImageUploadResponse(
        id=image.id,
        filename=image.filename,
        mime_type=image.mime_type,
        file_size_bytes=image.file_size_bytes,
    )


@router.get("/{image_id}", response_model=ImageMetadataResponse)
async def get_image(
    image_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    image_service: ImageService = Depends(get_image_service),
) -> ImageMetadataResponse:
    """Get image metadata by ID."""
    image = await image_service.get_image(session, image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    return ImageMetadataResponse(
        id=image.id,
        filename=image.filename,
        description=image.description,
        mime_type=image.mime_type,
        file_size_bytes=image.file_size_bytes,
        extracted_text=image.extracted_text,
        owner_id=image.owner_id,
        created_at=image.created_at,
        updated_at=image.updated_at,
    )


@router.get("", response_model=ImageListResponse)
async def list_images(
    owner_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    image_service: ImageService = Depends(get_image_service),
) -> ImageListResponse:
    """List images for a given owner."""
    images, total = await image_service.list_images(
        session=session,
        owner_id=owner_id,
        limit=limit,
        offset=offset,
    )

    return ImageListResponse(
        images=[
            ImageMetadataResponse(
                id=img.id,
                filename=img.filename,
                description=img.description,
                mime_type=img.mime_type,
                file_size_bytes=img.file_size_bytes,
                extracted_text=img.extracted_text,
                owner_id=img.owner_id,
                created_at=img.created_at,
                updated_at=img.updated_at,
            )
            for img in images
        ],
        total=total,
    )


@router.delete("/{image_id}", response_model=ImageDeleteResponse)
async def delete_image(
    image_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    image_service: ImageService = Depends(get_image_service),
) -> ImageDeleteResponse:
    """Delete an image by ID."""
    deleted = await image_service.delete_image(session, image_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Image not found")

    return ImageDeleteResponse(deleted=True, id=image_id)
