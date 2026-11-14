
import pytest
from unittest.mock import patch

from courtiq.domains.venues.extractor import VenuesExtractor


def test_extractor_returns_complexes():
    extractor = VenuesExtractor()

    data = extractor.extract()

    assert isinstance(data, dict)
    assert "complexes" in data
    assert isinstance(data["complexes"], list)
    assert len(data["complexes"]) > 0


def test_extractor_complexes_have_names():
    extractor = VenuesExtractor()

    data = extractor.extract()

    for complex_data in data["complexes"]:
        assert "name" in complex_data
        assert complex_data["name"]


def test_extractor_uses_demo_fixture():
    extractor = VenuesExtractor()

    data = extractor.extract()

    assert len(data["complexes"]) == 5
    assert data["complexes"][0]["name"] == "Melbourne Park"
