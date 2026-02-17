"""API routes for document management."""

import logging
import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.models.document import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
)
from app.services import document_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])


@router.post("", response_model=DocumentResponse, status_code=201)
async def create_document(
    document_data: DocumentCreate,
    session: AsyncSession = Depends(get_session),
) -> DocumentResponse:
    """
    Create a new document.

    Example request:
    ```json
    {
        "title": "Receipt - Grocery Store",
        "description": "Weekly groceries",
        "filename": "receipt_2024-01-15.pdf",
        "file_path": "/uploads/user123/receipt_2024-01-15.pdf",
        "file_size_bytes": 524288,
        "mime_type": "application/pdf",
        "owner_id": "123e4567-e89b-12d3-a456-426614174000"
    }
    ```
    """
    try:
        document = await document_service.create_document(session, document_data)
        return DocumentResponse.model_validate(document)
    except Exception as e:
        logger.error(
            f"Failed to create document: {type(e).__name__}",
            extra={"owner_id": str(document_data.owner_id)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to create document",
        ) from e


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    owner_id: uuid.UUID | None = Query(None, description="Filter by owner ID"),
    mime_type: str | None = Query(None, description="Filter by MIME type"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page (max 100)"),
    session: AsyncSession = Depends(get_session),
) -> DocumentListResponse:
    """
    List documents with optional filtering and pagination.

    Query parameters:
    - `owner_id`: Filter by owner UUID
    - `mime_type`: Filter by MIME type (e.g., "application/pdf")
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 50, max: 100)
    """
    try:
        documents, total = await document_service.list_documents(
            session=session,
            owner_id=owner_id,
            mime_type=mime_type,
            page=page,
            page_size=page_size,
        )

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return DocumentListResponse(
            documents=[DocumentResponse.model_validate(doc) for doc in documents],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except Exception as e:
        logger.error(
            f"Failed to list documents: {type(e).__name__}",
            extra={"owner_id": str(owner_id) if owner_id else None, "page": page},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to list documents",
        ) from e


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> DocumentResponse:
    """
    Get a single document by ID.
    """
    try:
        document = await document_service.get_document(session, document_id)
        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )
        return DocumentResponse.model_validate(document)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get document: {type(e).__name__}",
            extra={"document_id": str(document_id)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve document",
        ) from e


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: uuid.UUID,
    document_data: DocumentUpdate,
    session: AsyncSession = Depends(get_session),
) -> DocumentResponse:
    """
    Update a document with partial data.

    Example request:
    ```json
    {
        "title": "Updated Title",
        "description": "Updated description"
    }
    ```

    Only provided fields will be updated.
    """
    try:
        document = await document_service.update_document(session, document_id, document_data)
        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )
        return DocumentResponse.model_validate(document)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update document: {type(e).__name__}",
            extra={"document_id": str(document_id)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to update document",
        ) from e


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> None:
    """
    Delete a document.

    Returns 204 No Content on success, 404 if document not found.
    """
    try:
        deleted = await document_service.delete_document(session, document_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete document: {type(e).__name__}",
            extra={"document_id": str(document_id)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to delete document",
        ) from e
