"""Service layer for document operations."""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Document
from app.models.document import DocumentCreate, DocumentUpdate

logger = logging.getLogger(__name__)


async def create_document(session: AsyncSession, document_data: DocumentCreate) -> Document:
    """
    Create a new document in the database.

    Args:
        session: Database session
        document_data: Document creation data

    Returns:
        Created document ORM instance
    """
    document = Document(
        title=document_data.title,
        description=document_data.description,
        filename=document_data.filename,
        file_path=document_data.file_path,
        file_size_bytes=document_data.file_size_bytes,
        mime_type=document_data.mime_type,
        owner_id=document_data.owner_id,
    )

    session.add(document)
    await session.commit()
    await session.refresh(document)

    logger.info(
        f"Created document {document.id}",
        extra={"document_id": str(document.id), "owner_id": str(document_data.owner_id)},
    )

    return document


async def get_document(session: AsyncSession, document_id: uuid.UUID) -> Document | None:
    """
    Fetch a document by ID with its tags.

    Args:
        session: Database session
        document_id: Document UUID

    Returns:
        Document ORM instance or None if not found
    """
    stmt = select(Document).where(Document.id == document_id).options(selectinload(Document.tags))
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_documents(
    session: AsyncSession,
    owner_id: uuid.UUID | None = None,
    mime_type: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[Document], int]:
    """
    List documents with optional filtering and pagination.

    Args:
        session: Database session
        owner_id: Filter by owner UUID (optional)
        mime_type: Filter by MIME type (optional)
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (list of documents, total count)
    """
    # Base query
    stmt = select(Document).options(selectinload(Document.tags))

    # Apply filters
    if owner_id is not None:
        stmt = stmt.where(Document.owner_id == owner_id)
    if mime_type is not None:
        stmt = stmt.where(Document.mime_type == mime_type)

    # Count total matching documents
    count_stmt = select(Document)
    if owner_id is not None:
        count_stmt = count_stmt.where(Document.owner_id == owner_id)
    if mime_type is not None:
        count_stmt = count_stmt.where(Document.mime_type == mime_type)

    count_result = await session.execute(count_stmt)
    total = len(count_result.scalars().all())

    # Apply pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    # Execute query
    result = await session.execute(stmt)
    documents = list(result.scalars().all())

    logger.info(
        f"Listed {len(documents)} documents (page {page}, total {total})",
        extra={"page": page, "page_size": page_size, "total": total},
    )

    return documents, total


async def update_document(
    session: AsyncSession,
    document_id: uuid.UUID,
    document_data: DocumentUpdate,
) -> Document | None:
    """
    Update a document with partial data.

    Args:
        session: Database session
        document_id: Document UUID
        document_data: Partial update data

    Returns:
        Updated document ORM instance or None if not found
    """
    document = await get_document(session, document_id)
    if document is None:
        return None

    # Apply updates (only for non-None fields)
    update_data = document_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)

    await session.commit()
    await session.refresh(document)

    logger.info(
        f"Updated document {document_id}",
        extra={"document_id": str(document_id), "updated_fields": list(update_data.keys())},
    )

    return document


async def delete_document(session: AsyncSession, document_id: uuid.UUID) -> bool:
    """
    Delete a document from the database (hard delete).

    Args:
        session: Database session
        document_id: Document UUID

    Returns:
        True if document was deleted, False if not found
    """
    document = await get_document(session, document_id)
    if document is None:
        return False

    await session.delete(document)
    await session.commit()

    logger.info(f"Deleted document {document_id}", extra={"document_id": str(document_id)})

    return True
