"""Unit tests for DatabaseManager, connection pooling, and transaction lifecycle."""

import pytest
from sqlalchemy import text
from courtiq.core.database import DatabaseManager
from courtiq.core.exceptions import DatabaseError


def test_database_connection(test_db: DatabaseManager):
    """Verify database connection health and SQLite foreign keys when on SQLite."""
    assert test_db.check_health() is True
    with test_db.connection() as conn:
        if test_db._is_sqlite:
            row = conn.execute(text("PRAGMA foreign_keys;")).fetchone()
            assert row[0] == 1


def test_transaction_commit(test_db: DatabaseManager):
    """Verify changes inside transaction are committed upon successful block completion."""
    with test_db.transaction() as conn:
        conn.execute(
            text("INSERT INTO categories (category_id, category_name) VALUES (:category_id, :category_name);"),
            {"category_id": "sr:cat:test1", "category_name": "Test Cat"},
        )

    row = test_db.fetch_one(
        "SELECT * FROM categories WHERE category_id = :cat_id;",
        {"cat_id": "sr:cat:test1"},
    )
    assert row is not None
    assert row["category_name"] == "Test Cat"


def test_transaction_rollback(test_db: DatabaseManager):
    """Verify changes inside failed transaction are rolled back."""
    with pytest.raises(DatabaseError):
        with test_db.transaction() as conn:
            conn.execute(
                text("INSERT INTO categories (category_id, category_name) VALUES (:category_id, :category_name);"),
                {"category_id": "sr:cat:test2", "category_name": "Rollback Cat"},
            )
            # Trigger intentional syntax error to abort transaction
            conn.execute(text("INVALID SQL STATEMENT;"))

    row = test_db.fetch_one(
        "SELECT * FROM categories WHERE category_id = :cat_id;",
        {"cat_id": "sr:cat:test2"},
    )
    assert row is None


def test_execute_many(test_db: DatabaseManager):
    """Verify execute_many bulk inserts records atomically."""
    stmt = "INSERT INTO categories (category_id, category_name) VALUES (:category_id, :category_name);"
    params = [
        {"category_id": "sr:cat:m1", "category_name": "Many Cat 1"},
        {"category_id": "sr:cat:m2", "category_name": "Many Cat 2"},
    ]
    count = test_db.execute_many(stmt, params)
    assert count == 2

    records = test_db.fetch_all("SELECT * FROM categories WHERE category_id LIKE 'sr:cat:m%';")
    assert len(records) == 2


def test_fetch_df(test_db: DatabaseManager):
    """Verify fetch_df returns a pandas DataFrame."""
    test_db.execute(
        "INSERT INTO categories (category_id, category_name) VALUES (:id, :name);",
        {"id": "sr:cat:df1", "name": "DataFrame Cat"},
    )
    df = test_db.fetch_df(
        "SELECT category_id, category_name FROM categories WHERE category_id = :id;",
        {"id": "sr:cat:df1"},
    )
    assert not df.empty
    assert list(df.columns) == ["category_id", "category_name"]
    assert df.iloc[0]["category_name"] == "DataFrame Cat"


def test_migrations_tracking(test_db: DatabaseManager):
    """Verify applied migrations are recorded in alembic_version."""
    records = test_db.fetch_all("SELECT version_num FROM alembic_version;")
    assert len(records) >= 1
    versions = [r["version_num"] for r in records]
    assert any("0001" in v for v in versions)
