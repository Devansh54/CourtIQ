"""Unit tests for Rankings extractor."""

import pytest

from courtiq.domains.rankings.extractor import RankingsExtractor
from courtiq.core.exceptions import APIError


class MockAPIClient:
    def __init__(self, payload):
        self.payload = payload

    def get(self, endpoint):
        return self.payload


def test_extract_valid_rankings():
    payload = {
        "generated_at": "2024-11-04T12:00:00Z",
        "rankings": [
            {
                "name": "Doubles",
                "year": 2024,
                "week": 45,
                "competitor_rankings": [],
            }
        ],
    }

    extractor = RankingsExtractor(
        api_client=MockAPIClient(payload)
    )

    result = extractor.extract()

    assert result == payload
    assert "rankings" in result


def test_extract_invalid_payload():
    extractor = RankingsExtractor(
        api_client=MockAPIClient([])
    )

    with pytest.raises(APIError):
        extractor.extract()


def test_extract_missing_rankings_key():
    extractor = RankingsExtractor(
        api_client=MockAPIClient({"generated_at": "2024-11-04"})
    )

    with pytest.raises(APIError):
        extractor.extract()


def test_extract_rankings_not_list():
    extractor = RankingsExtractor(
        api_client=MockAPIClient({"rankings": "invalid"})
    )

    with pytest.raises(APIError):
        extractor.extract()


def test_extract_invalid_collection():
    extractor = RankingsExtractor(
        api_client=MockAPIClient({"rankings": ["invalid"]})
    )

    with pytest.raises(APIError):
        extractor.extract()