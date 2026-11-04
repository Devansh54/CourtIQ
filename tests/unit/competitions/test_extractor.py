"""Unit tests for Competitions API Extractor."""

from courtiq.domains.competitions.extractor import CompetitionsExtractor


def test_competitions_extractor_success():
    """Verify CompetitionsExtractor retrieves dictionary payload with competitions key."""
    extractor = CompetitionsExtractor()
    payload = extractor.extract()
    assert isinstance(payload, dict)
    assert "competitions" in payload
    assert len(payload["competitions"]) > 0
