"""Unit tests for database ORM models."""

import uuid

from app.db.models import Base, Document, DocumentTag, Tag, User


def test_user_model_has_correct_tablename():
    """Test User model table name."""
    assert User.__tablename__ == "users"


def test_document_model_has_correct_tablename():
    """Test Document model table name."""
    assert Document.__tablename__ == "documents"


def test_tag_model_has_correct_tablename():
    """Test Tag model table name."""
    assert Tag.__tablename__ == "tags"


def test_document_tag_model_has_correct_tablename():
    """Test DocumentTag association table name."""
    assert DocumentTag.__tablename__ == "document_tags"


def test_base_metadata_contains_all_tables():
    """Test that Base metadata knows about all tables."""
    table_names = set(Base.metadata.tables.keys())
    expected = {"users", "documents", "tags", "document_tags"}
    assert expected.issubset(table_names)


def test_user_repr():
    """Test User string representation."""
    user = User(id=uuid.uuid4(), email="test@example.com", display_name="Test User")
    assert "test@example.com" in repr(user)
    assert "User" in repr(user)


def test_document_repr():
    """Test Document string representation."""
    doc = Document(
        id=uuid.uuid4(),
        title="My Receipt",
        filename="receipt.pdf",
        file_path="/uploads/receipt.pdf",
        file_size_bytes=1024,
        owner_id=uuid.uuid4(),
    )
    assert "My Receipt" in repr(doc)
    assert "Document" in repr(doc)


def test_tag_repr():
    """Test Tag string representation."""
    tag = Tag(id=uuid.uuid4(), name="warranty")
    assert "warranty" in repr(tag)
    assert "Tag" in repr(tag)


def test_user_columns_exist():
    """Test that User model has expected columns."""
    column_names = {col.name for col in User.__table__.columns}
    expected = {"id", "email", "display_name", "created_at", "updated_at"}
    assert expected == column_names


def test_document_columns_exist():
    """Test that Document model has expected columns."""
    column_names = {col.name for col in Document.__table__.columns}
    expected = {
        "id",
        "title",
        "description",
        "filename",
        "file_path",
        "file_size_bytes",
        "mime_type",
        "extracted_text",
        "owner_id",
        "created_at",
        "updated_at",
    }
    assert expected == column_names


def test_tag_columns_exist():
    """Test that Tag model has expected columns."""
    column_names = {col.name for col in Tag.__table__.columns}
    expected = {"id", "name", "color", "created_at"}
    assert expected == column_names


def test_document_tags_columns_exist():
    """Test that DocumentTag model has expected columns."""
    column_names = {col.name for col in DocumentTag.__table__.columns}
    expected = {"document_id", "tag_id"}
    assert expected == column_names


def test_user_email_is_unique():
    """Test that email column has a unique constraint."""
    email_col = User.__table__.columns["email"]
    assert email_col.unique is True


def test_tag_name_is_unique():
    """Test that tag name column has a unique constraint."""
    name_col = Tag.__table__.columns["name"]
    assert name_col.unique is True


def test_document_owner_id_has_foreign_key():
    """Test that owner_id references users table."""
    owner_col = Document.__table__.columns["owner_id"]
    fk = list(owner_col.foreign_keys)
    assert len(fk) == 1
    assert fk[0].target_fullname == "users.id"
