"""Unit tests for Rankings repository."""

import pytest

from courtiq.domains.rankings.repository import RankingsRepository
from courtiq.domains.rankings.schemas import Competitor, CompetitorRanking


@pytest.fixture
def repository(test_db):
    return RankingsRepository(db_manager=test_db)


@pytest.fixture
def sample_competitor():
    return Competitor(
        competitor_id="test:competitor:001",
        name="Test Player",
        country="India",
        country_code="IND",
        abbreviation="TST",
    )


@pytest.fixture
def sample_ranking():
    return CompetitorRanking(
        rank=1,
        movement=2,
        points=5000,
        competitions_played=20,
        competitor_id="test:competitor:001",
    )


def test_save_and_count_competitor(
    repository, sample_competitor
):
    saved = repository.save_competitors([sample_competitor])

    assert saved == 1
    assert repository.get_competitor_count() == 1


def test_save_and_count_ranking(
    repository, sample_competitor, sample_ranking
):
    repository.save_competitors([sample_competitor])

    saved = repository.save_rankings([sample_ranking])

    assert saved == 1
    assert repository.get_rankings_count() == 1


def test_save_empty_competitors(repository):
    assert repository.save_competitors([]) == 0


def test_save_empty_rankings(repository):
    assert repository.save_rankings([]) == 0


def test_save_competitor_is_idempotent(
    repository, sample_competitor
):
    repository.save_competitors([sample_competitor])
    repository.save_competitors([sample_competitor])

    assert repository.get_competitor_count() == 1


def test_query_competitors_per_country(
    repository, sample_competitor, sample_ranking
):
    repository.save_competitors([sample_competitor])
    repository.save_rankings([sample_ranking])

    result = repository.query_5_competitors_per_country()

    assert not result.empty
    assert result.iloc[0]["country"] == "India"
    assert result.iloc[0]["total_competitors"] == 1