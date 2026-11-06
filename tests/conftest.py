"""CourtIQ Test Configuration & Shared Fixtures."""

import os
import json
from pathlib import Path
from typing import Any, Dict, Generator
import pytest

from courtiq.core.config import Settings
from courtiq.core.database import DatabaseManager


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def sample_competitions_payload(fixtures_dir: Path) -> Dict[str, Any]:
    """Load sample competitions fixture JSON."""
    file_path = fixtures_dir / "competitions_sample.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def sample_complexes_payload(fixtures_dir: Path) -> Dict[str, Any]:
    """Load sample complexes fixture JSON."""
    file_path = fixtures_dir / "complexes_sample.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def sample_rankings_payload(fixtures_dir: Path) -> Dict[str, Any]:
    """Load sample rankings fixture JSON."""
    file_path = fixtures_dir / "rankings_sample.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def postgres_test_db() -> Generator[DatabaseManager, None, None]:
    """Provide a verified PostgreSQL test database.
    
    Mandatory for PostgreSQL integration and concurrency tests.
    Does NOT silently fall back to SQLite: if TEST_DATABASE_URL is not configured,
    the test is reported as explicitly skipped (not executed).
    """
    test_url = os.getenv("TEST_DATABASE_URL")
    if not test_url:
        pytest.skip(
            "TEST_DATABASE_URL environment variable is not configured. "
            "Skipping PostgreSQL integration/concurrency test to prevent silent fallback to SQLite."
        )

    # Validate that it is a PostgreSQL connection
    if not test_url.lower().startswith("postgresql"):
        raise ValueError(
            f"TEST_DATABASE_URL must be a PostgreSQL connection string, got: {test_url.split(':')[0]}"
        )

    db_name = test_url.split("/")[-1].split("?")[0]
    db_mgr = DatabaseManager(test_url)

    # Enforce PostgreSQL dialect
    assert db_mgr.is_postgres is True, "Expected PostgreSQL connection"
    assert db_mgr.is_sqlite is False, "Silent SQLite connection detected"

    # Record detected dialect and database name without exposing credentials
    print(f"\n[PostgreSQL Test Environment] Dialect: {db_mgr._engine.dialect.name} | Database: {db_name}")

    db_mgr.run_migrations()
    try:
        yield db_mgr
    finally:
        try:
            db_mgr.execute("DELETE FROM competitions;")
            db_mgr.execute("DELETE FROM categories;")
        except Exception:
            pass
        try:
            db_mgr._engine.dispose()
        except Exception:
            pass


@pytest.fixture
def test_db(tmp_path: Path) -> Generator[DatabaseManager, None, None]:
    """Provide an isolated test database for unit tests.
    
    Prefers TEST_DATABASE_URL when available; falls back to an isolated
    temporary SQLite database for local offline unit tests.
    """
    test_url = os.getenv("TEST_DATABASE_URL")
    if test_url:
        db_mgr = DatabaseManager(test_url)
        db_mgr.run_migrations()
        try:
            yield db_mgr
        finally:
            try:
                db_mgr.execute("DELETE FROM competitions;")
                db_mgr.execute("DELETE FROM categories;")
            except Exception:
                pass
            try:
                db_mgr._engine.dispose()
            except Exception:
                pass
    else:
        db_file = tmp_path / "unit_test_courtiq.db"
        db_mgr = DatabaseManager(db_file)
        db_mgr.run_migrations()
        try:
            yield db_mgr
        finally:
            try:
                db_mgr._engine.dispose()
            except Exception:
                pass
