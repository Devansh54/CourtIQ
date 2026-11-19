"""Unit tests for Rankings domain schemas."""

import pytest
from pydantic import ValidationError

from courtiq.domains.rankings.schemas import (
    Competitor,
    CompetitorRanking,
)


def test_valid_competitor():
    competitor = Competitor(
        competitor_id="sr:competitor:123",
        name="Granollers, Marcel",
        country="Spain",
        country_code="esp",
        abbreviation="MAR",
    )

    assert competitor.name == "Granollers, Marcel"
    assert competitor.country_code == "ESP"


def test_competitor_removes_extra_spaces():
    competitor = Competitor(
        competitor_id=" sr:competitor:123 ",
        name=" Granollers, Marcel ",
        country=" Spain ",
        country_code="esp",
        abbreviation=" MAR ",
    )

    assert competitor.competitor_id == "sr:competitor:123"
    assert competitor.name == "Granollers, Marcel"
    assert competitor.country == "Spain"
    assert competitor.abbreviation == "MAR"


def test_invalid_competitor_id():
    with pytest.raises(ValidationError):
        Competitor(
            competitor_id="",
            name="Granollers, Marcel",
            country="Spain",
            country_code="ESP",
            abbreviation="MAR",
        )


def test_valid_competitor_ranking():
    ranking = CompetitorRanking(
        rank=1,
        movement=0,
        points=7820,
        competitions_played=22,
        competitor_id="sr:competitor:123",
    )

    assert ranking.rank == 1
    assert ranking.points == 7820
    assert ranking.movement == 0


def test_invalid_rank():
    with pytest.raises(ValidationError):
        CompetitorRanking(
            rank=0,
            movement=0,
            points=7820,
            competitions_played=22,
            competitor_id="sr:competitor:123",
        )


def test_negative_points_not_allowed():
    with pytest.raises(ValidationError):
        CompetitorRanking(
            rank=1,
            movement=0,
            points=-100,
            competitions_played=22,
            competitor_id="sr:competitor:123",
        )