"""Tag CRUD API routes."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.models.tag import TagCreate, TagListResponse, TagResponse, TagUpdate
from app.services.tag_service import TagService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tags", tags=["Tags"])


def get_tag_service(session: AsyncSession = Depends(get_session)) -> TagService:
    """Dependency injection for TagService."""
    return TagService(session)


@router.post(
    "",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a tag",
)
async def create_tag(
    data: TagCreate,
    service: TagService = Depends(get_tag_service),
) -> TagResponse:
    """Create a new tag."""
    try:
        tag = await service.create_tag(data)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A tag with name '{data.name}' already exists",
        ) from exc
    return TagResponse.model_validate(tag)


@router.get(
    "",
    response_model=TagListResponse,
    summary="List tags",
)
async def list_tags(
    limit: int = Query(default=20, ge=1, le=100, description="Page size"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
    service: TagService = Depends(get_tag_service),
) -> TagListResponse:
    """List all tags with pagination."""
    tags, total = await service.list_tags(limit=limit, offset=offset)
    return TagListResponse(
        items=[TagResponse.model_validate(t) for t in tags],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{tag_id}",
    response_model=TagResponse,
    summary="Get a tag",
)
async def get_tag(
    tag_id: uuid.UUID,
    service: TagService = Depends(get_tag_service),
) -> TagResponse:
    """Fetch a single tag by ID."""
    tag = await service.get_tag(tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    return TagResponse.model_validate(tag)


@router.patch(
    "/{tag_id}",
    response_model=TagResponse,
    summary="Update a tag",
)
async def update_tag(
    tag_id: uuid.UUID,
    data: TagUpdate,
    service: TagService = Depends(get_tag_service),
) -> TagResponse:
    """Partially update a tag."""
    try:
        tag = await service.update_tag(tag_id, data)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A tag with name '{data.name}' already exists",
        ) from exc

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    return TagResponse.model_validate(tag)


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a tag",
)
async def delete_tag(
    tag_id: uuid.UUID,
    service: TagService = Depends(get_tag_service),
) -> None:
    """Delete a tag by ID."""
    deleted = await service.delete_tag(tag_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
