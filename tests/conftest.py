"""CourtIQ Test Configuration & Shared Fixtures."""

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
def test_db(tmp_path: Path) -> Generator[DatabaseManager, None, None]:
    """Provide an isolated, fully migrated test SQLite database in temporary path."""
    db_file = tmp_path / "test_courtiq.db"
    db_mgr = DatabaseManager(db_file)
    # Apply migrations
    migrations_dir = Path(__file__).resolve().parent.parent / "sql" / "migrations"
    db_mgr.run_migrations(migrations_dir)
    yield db_mgr
