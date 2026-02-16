"""Memo CRUD route handlers."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.models.memo import MemoCreate, MemoListResponse, MemoResponse, MemoUpdate
from app.services.memo_service import MemoService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/memos", tags=["Memos"])


def _get_memo_service(session: AsyncSession = Depends(get_session)) -> MemoService:
    """Dependency that provides a MemoService bound to the current DB session."""
    return MemoService(session)


@router.post("", response_model=MemoResponse, status_code=201)
async def create_memo(
    body: MemoCreate,
    service: MemoService = Depends(_get_memo_service),
) -> MemoResponse:
    """Create a new memo/note."""
    return await service.create_memo(body)


@router.get("", response_model=MemoListResponse)
async def list_memos(
    tag: str | None = Query(None, description="Filter by tag"),
    search: str | None = Query(None, description="Search in title and content"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Max items to return"),
    service: MemoService = Depends(_get_memo_service),
) -> MemoListResponse:
    """List memos with optional tag/search filtering."""
    return await service.list_memos(tag=tag, search=search, offset=offset, limit=limit)


@router.get("/{memo_id}", response_model=MemoResponse)
async def get_memo(
    memo_id: uuid.UUID,
    service: MemoService = Depends(_get_memo_service),
) -> MemoResponse:
    """Retrieve a single memo by ID."""
    memo = await service.get_memo(memo_id)
    if memo is None:
        raise HTTPException(status_code=404, detail="Memo not found")
    return memo


@router.patch("/{memo_id}", response_model=MemoResponse)
async def update_memo(
    memo_id: uuid.UUID,
    body: MemoUpdate,
    service: MemoService = Depends(_get_memo_service),
) -> MemoResponse:
    """Update an existing memo (partial update)."""
    memo = await service.update_memo(memo_id, body)
    if memo is None:
        raise HTTPException(status_code=404, detail="Memo not found")
    return memo


@router.delete("/{memo_id}", status_code=204)
async def delete_memo(
    memo_id: uuid.UUID,
    service: MemoService = Depends(_get_memo_service),
) -> None:
    """Delete a memo."""
    deleted = await service.delete_memo(memo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memo not found")
