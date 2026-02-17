"""Unit tests for document Pydantic models."""

import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.document import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
    TagResponse,
)


def test_document_create_valid():
    """Test DocumentCreate with valid data."""
    owner_id = uuid.uuid4()
    doc = DocumentCreate(
        title="Test Document",
        description="A test document",
        filename="test.pdf",
        file_path="/uploads/test.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
        owner_id=owner_id,
    )

    assert doc.title == "Test Document"
    assert doc.description == "A test document"
    assert doc.filename == "test.pdf"
    assert doc.file_path == "/uploads/test.pdf"
    assert doc.file_size_bytes == 1024
    assert doc.mime_type == "application/pdf"
    assert doc.owner_id == owner_id


def test_document_create_without_description():
    """Test DocumentCreate without optional description field."""
    owner_id = uuid.uuid4()
    doc = DocumentCreate(
        title="Test Document",
        filename="test.pdf",
        file_path="/uploads/test.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
        owner_id=owner_id,
    )

    assert doc.description is None


def test_document_create_empty_title_fails():
    """Test DocumentCreate with empty title fails validation."""
    owner_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        DocumentCreate(
            title="",  # Empty string should fail
            filename="test.pdf",
            file_path="/uploads/test.pdf",
            file_size_bytes=1024,
            mime_type="application/pdf",
            owner_id=owner_id,
        )


def test_document_create_negative_file_size_fails():
    """Test DocumentCreate with negative file size fails validation."""
    owner_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        DocumentCreate(
            title="Test",
            filename="test.pdf",
            file_path="/uploads/test.pdf",
            file_size_bytes=-1,  # Negative should fail
            mime_type="application/pdf",
            owner_id=owner_id,
        )


def test_document_create_zero_file_size_fails():
    """Test DocumentCreate with zero file size fails validation."""
    owner_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        DocumentCreate(
            title="Test",
            filename="test.pdf",
            file_path="/uploads/test.pdf",
            file_size_bytes=0,  # Zero should fail
            mime_type="application/pdf",
            owner_id=owner_id,
        )


def test_document_update_all_fields_optional():
    """Test DocumentUpdate with all fields optional."""
    # Empty update is valid
    update = DocumentUpdate()
    assert update.title is None
    assert update.description is None
    assert update.filename is None
    assert update.file_path is None
    assert update.file_size_bytes is None
    assert update.mime_type is None


def test_document_update_partial():
    """Test DocumentUpdate with partial data."""
    update = DocumentUpdate(
        title="Updated Title",
        description="Updated description",
    )

    assert update.title == "Updated Title"
    assert update.description == "Updated description"
    assert update.filename is None


def test_document_update_empty_title_fails():
    """Test DocumentUpdate with empty title fails validation."""
    with pytest.raises(ValidationError):
        DocumentUpdate(title="")  # Empty string should fail


def test_tag_response_valid():
    """Test TagResponse with valid data."""
    tag_id = uuid.uuid4()
    tag = TagResponse(
        id=tag_id,
        name="receipt",
        color="#FF5733",
    )

    assert tag.id == tag_id
    assert tag.name == "receipt"
    assert tag.color == "#FF5733"


def test_tag_response_without_color():
    """Test TagResponse without optional color field."""
    tag_id = uuid.uuid4()
    tag = TagResponse(
        id=tag_id,
        name="receipt",
    )

    assert tag.color is None


def test_document_response_valid():
    """Test DocumentResponse with valid data."""
    doc_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    now = datetime.now()

    doc = DocumentResponse(
        id=doc_id,
        title="Test Document",
        description="A test",
        filename="test.pdf",
        file_path="/uploads/test.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
        owner_id=owner_id,
        created_at=now,
        updated_at=now,
        tags=[],
    )

    assert doc.id == doc_id
    assert doc.title == "Test Document"
    assert doc.owner_id == owner_id
    assert doc.tags == []


def test_document_response_with_tags():
    """Test DocumentResponse with associated tags."""
    doc_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    tag_id = uuid.uuid4()
    now = datetime.now()

    doc = DocumentResponse(
        id=doc_id,
        title="Test Document",
        filename="test.pdf",
        file_path="/uploads/test.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
        owner_id=owner_id,
        created_at=now,
        updated_at=now,
        tags=[
            TagResponse(id=tag_id, name="receipt", color="#FF5733"),
        ],
    )

    assert len(doc.tags) == 1
    assert doc.tags[0].name == "receipt"


def test_document_list_response_valid():
    """Test DocumentListResponse with valid data."""
    doc_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    now = datetime.now()

    doc = DocumentResponse(
        id=doc_id,
        title="Test Document",
        filename="test.pdf",
        file_path="/uploads/test.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
        owner_id=owner_id,
        created_at=now,
        updated_at=now,
        tags=[],
    )

    response = DocumentListResponse(
        documents=[doc],
        total=1,
        page=1,
        page_size=50,
        total_pages=1,
    )

    assert len(response.documents) == 1
    assert response.total == 1
    assert response.page == 1
    assert response.page_size == 50
    assert response.total_pages == 1


def test_document_list_response_empty():
    """Test DocumentListResponse with no documents."""
    response = DocumentListResponse(
        documents=[],
        total=0,
        page=1,
        page_size=50,
        total_pages=0,
    )

    assert response.documents == []
    assert response.total == 0


def test_document_list_response_pagination():
    """Test DocumentListResponse with pagination."""
    response = DocumentListResponse(
        documents=[],
        total=150,
        page=2,
        page_size=50,
        total_pages=3,
    )

    assert response.total == 150
    assert response.page == 2
    assert response.page_size == 50
    assert response.total_pages == 3
