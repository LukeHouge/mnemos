"""Unit tests for document service."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.models import Document
from app.models.document import DocumentCreate, DocumentUpdate
from app.services import document_service


@pytest.fixture
def mock_session():
    """Create a mock AsyncSession."""
    session = AsyncMock()
    return session


@pytest.fixture
def sample_document():
    """Create a sample document ORM instance."""
    doc = Document(
        id=uuid.uuid4(),
        title="Test Document",
        description="Test description",
        filename="test.pdf",
        file_path="/uploads/test.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
        owner_id=uuid.uuid4(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    doc.tags = []
    return doc


@pytest.fixture
def sample_document_create():
    """Create a sample DocumentCreate instance."""
    return DocumentCreate(
        title="Test Document",
        description="Test description",
        filename="test.pdf",
        file_path="/uploads/test.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
        owner_id=uuid.uuid4(),
    )


async def test_create_document_success(mock_session, sample_document_create):
    """Test successful document creation."""
    # Setup
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Execute
    result = await document_service.create_document(mock_session, sample_document_create)

    # Assert
    assert result.title == sample_document_create.title
    assert result.filename == sample_document_create.filename
    assert result.owner_id == sample_document_create.owner_id
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


async def test_get_document_found(mock_session, sample_document):
    """Test getting an existing document."""
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_document
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Execute
    result = await document_service.get_document(mock_session, sample_document.id)

    # Assert
    assert result is not None
    assert result.id == sample_document.id
    assert result.title == sample_document.title
    mock_session.execute.assert_called_once()


async def test_get_document_not_found(mock_session):
    """Test getting a non-existent document."""
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Execute
    result = await document_service.get_document(mock_session, uuid.uuid4())

    # Assert
    assert result is None
    mock_session.execute.assert_called_once()


async def test_list_documents_no_filters(mock_session, sample_document):
    """Test listing documents without filters."""
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [sample_document]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Execute
    documents, total = await document_service.list_documents(mock_session)

    # Assert
    assert len(documents) == 1
    assert total == 1
    assert documents[0].id == sample_document.id
    # Called twice: once for count, once for actual query
    assert mock_session.execute.call_count == 2


async def test_list_documents_with_owner_filter(mock_session, sample_document):
    """Test listing documents filtered by owner."""
    # Setup
    owner_id = sample_document.owner_id
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [sample_document]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Execute
    documents, total = await document_service.list_documents(mock_session, owner_id=owner_id)

    # Assert
    assert len(documents) == 1
    assert documents[0].owner_id == owner_id


async def test_list_documents_with_mime_type_filter(mock_session, sample_document):
    """Test listing documents filtered by MIME type."""
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [sample_document]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Execute
    documents, total = await document_service.list_documents(
        mock_session, mime_type="application/pdf"
    )

    # Assert
    assert len(documents) == 1
    assert documents[0].mime_type == "application/pdf"


async def test_list_documents_with_pagination(mock_session, sample_document):
    """Test listing documents with pagination."""
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [sample_document]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Execute
    documents, total = await document_service.list_documents(
        mock_session, page=2, page_size=10
    )

    # Assert
    assert len(documents) == 1
    # Verify pagination was applied (offset and limit)
    assert mock_session.execute.call_count == 2


async def test_list_documents_empty_result(mock_session):
    """Test listing documents when no documents exist."""
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Execute
    documents, total = await document_service.list_documents(mock_session)

    # Assert
    assert len(documents) == 0
    assert total == 0


async def test_update_document_success(mock_session, sample_document):
    """Test successful document update."""
    # Setup
    update_data = DocumentUpdate(title="Updated Title", description="Updated description")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_document
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Execute
    result = await document_service.update_document(mock_session, sample_document.id, update_data)

    # Assert
    assert result is not None
    assert result.title == "Updated Title"
    assert result.description == "Updated description"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


async def test_update_document_partial(mock_session, sample_document):
    """Test partial document update."""
    # Setup
    original_filename = sample_document.filename
    update_data = DocumentUpdate(title="Updated Title")  # Only update title
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_document
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Execute
    result = await document_service.update_document(mock_session, sample_document.id, update_data)

    # Assert
    assert result is not None
    assert result.title == "Updated Title"
    assert result.filename == original_filename  # Should remain unchanged


async def test_update_document_not_found(mock_session):
    """Test updating a non-existent document."""
    # Setup
    update_data = DocumentUpdate(title="Updated Title")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Execute
    result = await document_service.update_document(mock_session, uuid.uuid4(), update_data)

    # Assert
    assert result is None
    # Should not attempt to commit
    mock_session.commit.assert_not_called()


async def test_delete_document_success(mock_session, sample_document):
    """Test successful document deletion."""
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_document
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()

    # Execute
    result = await document_service.delete_document(mock_session, sample_document.id)

    # Assert
    assert result is True
    mock_session.delete.assert_called_once_with(sample_document)
    mock_session.commit.assert_called_once()


async def test_delete_document_not_found(mock_session):
    """Test deleting a non-existent document."""
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Execute
    result = await document_service.delete_document(mock_session, uuid.uuid4())

    # Assert
    assert result is False
    # Should not attempt to delete or commit
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
