"""Unit tests for document API routes."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from app.db.models import Document
from app.main import app
from app.routes.documents import get_session


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
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


def test_create_document_success(client, mock_db_session, sample_document):
    """Test successful document creation."""
    # Override dependency
    app.dependency_overrides[get_session] = lambda: mock_db_session

    try:
        # Mock service call
        with patch("app.routes.documents.document_service.create_document") as mock_create:
            mock_create.return_value = sample_document

            # Make request
            response = client.post(
                "/api/v1/documents",
                json={
                    "title": "Test Document",
                    "description": "Test description",
                    "filename": "test.pdf",
                    "file_path": "/uploads/test.pdf",
                    "file_size_bytes": 1024,
                    "mime_type": "application/pdf",
                    "owner_id": str(sample_document.owner_id),
                },
            )

            # Assertions
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Test Document"
            assert data["filename"] == "test.pdf"
    finally:
        app.dependency_overrides.clear()


def test_create_document_validation_error(client):
    """Test document creation with invalid data."""
    # Missing required fields
    response = client.post(
        "/api/v1/documents",
        json={
            "title": "Test",
            # Missing other required fields
        },
    )

    assert response.status_code == 422


def test_create_document_empty_title(client):
    """Test document creation with empty title."""
    response = client.post(
        "/api/v1/documents",
        json={
            "title": "",  # Empty title
            "filename": "test.pdf",
            "file_path": "/uploads/test.pdf",
            "file_size_bytes": 1024,
            "mime_type": "application/pdf",
            "owner_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 422


def test_get_document_success(client, mock_db_session, sample_document):
    """Test getting a document by ID."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    try:
        with patch("app.routes.documents.document_service.get_document") as mock_get:
            mock_get.return_value = sample_document

            response = client.get(f"/api/v1/documents/{sample_document.id}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(sample_document.id)
            assert data["title"] == sample_document.title
    finally:
        app.dependency_overrides.clear()


def test_get_document_not_found(client, mock_db_session):
    """Test getting a non-existent document."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    try:
        with patch("app.routes.documents.document_service.get_document") as mock_get:
            mock_get.return_value = None

            response = client.get(f"/api/v1/documents/{uuid.uuid4()}")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


def test_list_documents_success(client, mock_db_session, sample_document):
    """Test listing documents."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    try:
        with patch("app.routes.documents.document_service.list_documents") as mock_list:
            mock_list.return_value = ([sample_document], 1)

            response = client.get("/api/v1/documents")

            assert response.status_code == 200
            data = response.json()
            assert len(data["documents"]) == 1
            assert data["total"] == 1
            assert data["page"] == 1
            assert data["page_size"] == 50
            assert data["total_pages"] == 1
    finally:
        app.dependency_overrides.clear()


def test_list_documents_with_filters(client, mock_db_session, sample_document):
    """Test listing documents with filters."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    try:
        with patch("app.routes.documents.document_service.list_documents") as mock_list:
            mock_list.return_value = ([sample_document], 1)

            response = client.get(
                "/api/v1/documents",
                params={
                    "owner_id": str(sample_document.owner_id),
                    "mime_type": "application/pdf",
                    "page": 1,
                    "page_size": 10,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["documents"]) == 1
    finally:
        app.dependency_overrides.clear()


def test_list_documents_empty(client, mock_db_session):
    """Test listing documents when none exist."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    try:
        with patch("app.routes.documents.document_service.list_documents") as mock_list:
            mock_list.return_value = ([], 0)

            response = client.get("/api/v1/documents")

            assert response.status_code == 200
            data = response.json()
            assert data["documents"] == []
            assert data["total"] == 0
            assert data["total_pages"] == 0
    finally:
        app.dependency_overrides.clear()


def test_list_documents_pagination(client, mock_db_session, sample_document):
    """Test listing documents with pagination."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    try:
        with patch("app.routes.documents.document_service.list_documents") as mock_list:
            # Simulate 150 total documents, page 2 of 3
            mock_list.return_value = ([sample_document], 150)

            response = client.get(
                "/api/v1/documents",
                params={"page": 2, "page_size": 50},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["page"] == 2
            assert data["page_size"] == 50
            assert data["total"] == 150
            assert data["total_pages"] == 3
    finally:
        app.dependency_overrides.clear()


def test_update_document_success(client, mock_db_session, sample_document):
    """Test updating a document."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    try:
        updated_doc = sample_document
        updated_doc.title = "Updated Title"

        with patch("app.routes.documents.document_service.update_document") as mock_update:
            mock_update.return_value = updated_doc

            response = client.patch(
                f"/api/v1/documents/{sample_document.id}",
                json={"title": "Updated Title"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Updated Title"
    finally:
        app.dependency_overrides.clear()


def test_update_document_not_found(client, mock_db_session):
    """Test updating a non-existent document."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    try:
        with patch("app.routes.documents.document_service.update_document") as mock_update:
            mock_update.return_value = None

            response = client.patch(
                f"/api/v1/documents/{uuid.uuid4()}",
                json={"title": "Updated Title"},
            )

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


def test_update_document_validation_error(client):
    """Test updating a document with invalid data."""
    response = client.patch(
        f"/api/v1/documents/{uuid.uuid4()}",
        json={"title": ""},  # Empty title should fail
    )

    assert response.status_code == 422


def test_delete_document_success(client, mock_db_session, sample_document):
    """Test deleting a document."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    try:
        with patch("app.routes.documents.document_service.delete_document") as mock_delete:
            mock_delete.return_value = True

            response = client.delete(f"/api/v1/documents/{sample_document.id}")

            assert response.status_code == 204
    finally:
        app.dependency_overrides.clear()


def test_delete_document_not_found(client, mock_db_session):
    """Test deleting a non-existent document."""
    app.dependency_overrides[get_session] = lambda: mock_db_session

    try:
        with patch("app.routes.documents.document_service.delete_document") as mock_delete:
            mock_delete.return_value = False

            response = client.delete(f"/api/v1/documents/{uuid.uuid4()}")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()
