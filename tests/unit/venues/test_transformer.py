
from courtiq.domains.venues.extractor import VenuesExtractor
from courtiq.domains.venues.transformer import VenuesTransformer


def test_transformer_returns_complexes_and_venues():
    raw_data = VenuesExtractor().extract()

    complexes, venues = VenuesTransformer().transform(raw_data)

    assert isinstance(complexes, list)
    assert isinstance(venues, list)
    assert len(complexes) > 0
    assert len(venues) > 0


def test_transformer_expected_record_counts():
    raw_data = VenuesExtractor().extract()

    complexes, venues = VenuesTransformer().transform(raw_data)

    assert len(complexes) == 5
    assert len(venues) == 11


def test_transformer_venue_has_complex_reference():
    raw_data = VenuesExtractor().extract()

    complexes, venues = VenuesTransformer().transform(raw_data)

    complex_ids = {item.complex_id for item in complexes}

    for venue in venues:
        assert venue.complex_id in complex_ids
