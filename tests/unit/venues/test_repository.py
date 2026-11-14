
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd
import pytest

from courtiq.domains.venues.repository import VenuesRepository
from courtiq.domains.venues.schemas import Complex, Venue


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def repository(mock_db, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "courtiq.domains.venues.repository.get_settings",
        lambda: SimpleNamespace(project_root=tmp_path),
    )

    return VenuesRepository(db_manager=mock_db)


def test_save_complexes(repository, mock_db):
    complexes = [
        Complex(complex_id="sr:complex:1", complex_name="Melbourne Park")
    ]

    mock_db.execute_many.return_value = 1

    result = repository.save_complexes(complexes)

    assert result == 1
    mock_db.execute_many.assert_called_once()


def test_save_complexes_empty_list(repository, mock_db):
    result = repository.save_complexes([])

    assert result == 0
    mock_db.execute_many.assert_not_called()


def test_save_venues(repository, mock_db):
    venues = [
        Venue(
            venue_id="sr:venue:1",
            venue_name="Rod Laver Arena",
            city_name="Melbourne",
            country_name="Australia",
            country_code="AUS",
            timezone="Australia/Melbourne",
            complex_id="sr:complex:1",
        )
    ]

    mock_db.execute_many.return_value = 1

    result = repository.save_venues(venues)

    assert result == 1
    mock_db.execute_many.assert_called_once()


def test_save_venues_empty_list(repository, mock_db):
    result = repository.save_venues([])

    assert result == 0
    mock_db.execute_many.assert_not_called()


def test_get_complex_count(repository, mock_db):
    mock_db.fetch_one.return_value = {"count": 5}

    assert repository.get_complex_count() == 5


def test_get_venue_count(repository, mock_db):
    mock_db.fetch_one.return_value = {"count": 11}

    assert repository.get_venue_count() == 11


def test_count_returns_zero_when_no_result(repository, mock_db):
    mock_db.fetch_one.return_value = None

    assert repository.get_complex_count() == 0
    assert repository.get_venue_count() == 0


def test_read_query(repository, tmp_path):
    query_file = tmp_path / "sql" / "queries" / "venues"
    query_file.mkdir(parents=True)

    sql_file = query_file / "sample.sql"
    sql_file.write_text("SELECT 1;", encoding="utf-8")

    assert repository._read_query("sample.sql") == "SELECT 1;"


def test_read_query_missing_file(repository):
    with pytest.raises(FileNotFoundError):
        repository._read_query("missing.sql")


@pytest.mark.parametrize(
    "method_name",
    [
        "query_1_venues_with_complex",
        "query_2_venues_count_per_complex",
        "query_3_venues_by_country",
        "query_4_venues_and_timezones",
        "query_5_multi_venue_complexes",
        "query_6_venues_by_country_group",
        "query_7_venues_for_specific_complex",
    ],
)
def test_query_methods_return_dataframe(
    repository, mock_db, tmp_path, method_name
):
    query_dir = tmp_path / "sql" / "queries" / "venues"
    query_dir.mkdir(parents=True)

    for number in range(1, 8):
        (query_dir / f"q{number}_").write_text(
            "SELECT 1;", encoding="utf-8"
        ) if False else None

    query_files = [
        "q1_venues_with_complex.sql",
        "q2_venues_count_per_complex.sql",
        "q3_venues_by_country.sql",
        "q4_venues_and_timezones.sql",
        "q5_multi_venue_complexes.sql",
        "q6_venues_by_country_group.sql",
        "q7_venues_for_specific_complex.sql",
    ]

    for filename in query_files:
        (query_dir / filename).write_text(
            "SELECT 1;", encoding="utf-8"
        )

    expected = pd.DataFrame({"result": [1]})
    mock_db.fetch_df.return_value = expected

    result = getattr(repository, method_name)()

    assert isinstance(result, pd.DataFrame)
    assert result.equals(expected)
    mock_db.fetch_df.assert_called_once()
