"""Unit tests for DatabaseManager and transaction lifecycle."""

import pytest
from courtiq.core.database import DatabaseManager
from courtiq.core.exceptions import DatabaseError


def test_database_connection(test_db: DatabaseManager):
    """Verify connection and foreign keys are active."""
    with test_db.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys;")
        row = cursor.fetchone()
        assert row[0] == 1


def test_transaction_commit(test_db: DatabaseManager):
    """Verify changes inside transaction are committed upon successful block completion."""
    with test_db.transaction() as conn:
        conn.execute("INSERT INTO categories (category_id, category_name) VALUES (?, ?);", ("sr:cat:test1", "Test Cat"))

    row = test_db.fetch_one("SELECT * FROM categories WHERE category_id = ?;", ("sr:cat:test1",))
    assert row is not None
    assert row["category_name"] == "Test Cat"


def test_transaction_rollback(test_db: DatabaseManager):
    """Verify changes inside failed transaction are rolled back."""
    with pytest.raises(DatabaseError):
        with test_db.transaction() as conn:
            conn.execute("INSERT INTO categories (category_id, category_name) VALUES (?, ?);", ("sr:cat:test2", "Rollback Cat"))
            # Trigger intentional syntax error to abort transaction
            conn.execute("INVALID SQL STATEMENT;")

    row = test_db.fetch_one("SELECT * FROM categories WHERE category_id = ?;", ("sr:cat:test2",))
    assert row is None


def test_migrations_tracking(test_db: DatabaseManager):
    """Verify applied migrations are recorded in schema_migrations."""
    records = test_db.fetch_all("SELECT version FROM schema_migrations;")
    assert len(records) >= 1
    versions = [r["version"] for r in records]
    assert "001_competitions.sql" in versions
