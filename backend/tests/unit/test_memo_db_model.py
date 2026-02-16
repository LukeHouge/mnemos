"""Unit tests for Memo ORM model."""

import uuid

from app.db.models import Base, Memo


def test_memo_model_has_correct_tablename():
    """Test Memo model table name."""
    assert Memo.__tablename__ == "memos"


def test_memo_columns_exist():
    """Test that Memo model has expected columns."""
    column_names = {col.name for col in Memo.__table__.columns}
    expected = {"id", "title", "content", "tags", "created_at", "updated_at"}
    assert expected == column_names


def test_memo_repr():
    """Test Memo string representation."""
    memo = Memo(id=uuid.uuid4(), title="My Note", content="Some text")
    assert "My Note" in repr(memo)
    assert "Memo" in repr(memo)


def test_memo_repr_without_title():
    """Test Memo repr when title is None."""
    memo = Memo(id=uuid.uuid4(), title=None, content="Some text")
    assert "Memo" in repr(memo)
    assert "None" in repr(memo)


def test_base_metadata_contains_memos_table():
    """Test that Base metadata knows about the memos table."""
    table_names = set(Base.metadata.tables.keys())
    assert "memos" in table_names


def test_memo_content_is_not_nullable():
    """Test that content column is not nullable."""
    content_col = Memo.__table__.columns["content"]
    assert content_col.nullable is False


def test_memo_title_is_nullable():
    """Test that title column is nullable."""
    title_col = Memo.__table__.columns["title"]
    assert title_col.nullable is True


def test_memo_tags_is_not_nullable():
    """Test that tags column is not nullable."""
    tags_col = Memo.__table__.columns["tags"]
    assert tags_col.nullable is False
