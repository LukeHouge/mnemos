"""Service layer for memo CRUD operations."""

import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Memo
from app.models.memo import MemoCreate, MemoListResponse, MemoResponse, MemoUpdate

logger = logging.getLogger(__name__)


class MemoService:
    """Handles memo persistence and retrieval."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_memo(self, data: MemoCreate) -> MemoResponse:
        """Create a new memo and return it."""
        memo = Memo(
            title=data.title,
            content=data.content,
            tags=data.tags,
        )
        self._session.add(memo)
        await self._session.commit()
        await self._session.refresh(memo)
        logger.info("Memo created", extra={"memo_id": str(memo.id)})
        return _to_response(memo)

    async def get_memo(self, memo_id: uuid.UUID) -> MemoResponse | None:
        """Retrieve a single memo by ID. Returns None if not found."""
        memo = await self._session.get(Memo, memo_id)
        if memo is None:
            return None
        return _to_response(memo)

    async def list_memos(
        self,
        tag: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> MemoListResponse:
        """List memos with optional filtering by tag or text search."""
        query = select(Memo)
        count_query = select(func.count()).select_from(Memo)

        if tag is not None:
            query = query.where(Memo.tags.any(tag))  # type: ignore[attr-defined]
            count_query = count_query.where(Memo.tags.any(tag))  # type: ignore[attr-defined]

        if search is not None:
            pattern = f"%{search}%"
            search_filter = Memo.content.ilike(pattern) | Memo.title.ilike(pattern)
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Memo.updated_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(query)
        memos = list(result.scalars().all())

        return MemoListResponse(
            memos=[_to_response(m) for m in memos],
            total=total,
        )

    async def update_memo(self, memo_id: uuid.UUID, data: MemoUpdate) -> MemoResponse | None:
        """Update an existing memo. Returns None if not found."""
        memo = await self._session.get(Memo, memo_id)
        if memo is None:
            return None

        update_fields = data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(memo, field, value)

        await self._session.commit()
        await self._session.refresh(memo)
        logger.info("Memo updated", extra={"memo_id": str(memo.id)})
        return _to_response(memo)

    async def delete_memo(self, memo_id: uuid.UUID) -> bool:
        """Delete a memo. Returns True if deleted, False if not found."""
        memo = await self._session.get(Memo, memo_id)
        if memo is None:
            return False

        await self._session.delete(memo)
        await self._session.commit()
        logger.info("Memo deleted", extra={"memo_id": str(memo_id)})
        return True


def _to_response(memo: Memo) -> MemoResponse:
    """Convert a Memo ORM instance to a MemoResponse."""
    return MemoResponse(
        id=memo.id,
        title=memo.title,
        content=memo.content,
        tags=memo.tags,
        created_at=memo.created_at,
        updated_at=memo.updated_at,
    )
