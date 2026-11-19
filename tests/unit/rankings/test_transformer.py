"""Unit tests for Rankings transformer."""

import pytest

from courtiq.domains.rankings.transformer import RankingsTransformer
from courtiq.core.exceptions import TransformationError


@pytest.fixture
def sample_payload():
    return {
        "rankings": [
            {
                "competitor_rankings": [
                    {
                        "rank": 1,
                        "movement": 2,
                        "points": 7820,
                        "competitions_played": 22,
                        "competitor": {
                            "id": "sr:competitor:123",
                            "name": "Granollers, Marcel",
                            "country": "Spain",
                            "country_code": "ESP",
                            "abbreviation": "MAR",
                        },
                    }
                ]
            }
        ]
    }


def test_transform_valid_payload(sample_payload):
    transformer = RankingsTransformer()

    competitors, rankings = transformer.transform(sample_payload)

    assert len(competitors) == 1
    assert len(rankings) == 1
    assert competitors[0].name == "Granollers, Marcel"
    assert rankings[0].rank == 1
    assert rankings[0].points == 7820


def test_transform_invalid_payload():
    transformer = RankingsTransformer()

    with pytest.raises(TransformationError):
        transformer.transform([])


def test_transform_missing_rankings():
    transformer = RankingsTransformer()

    with pytest.raises(TransformationError):
        transformer.transform({})


def test_transform_invalid_competitor():
    transformer = RankingsTransformer()

    payload = {
        "rankings": [
            {
                "competitor_rankings": [
                    {
                        "rank": 1,
                        "movement": 0,
                        "points": 100,
                        "competitions_played": 10,
                        "competitor": {},
                    }
                ]
            }
        ]
    }

    with pytest.raises(TransformationError):
        transformer.transform(payload)