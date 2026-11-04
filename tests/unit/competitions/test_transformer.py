"""Unit tests for CompetitionsTransformer."""

from courtiq.domains.competitions.transformer import CompetitionsTransformer


def test_transformer_success(sample_competitions_payload):
    """Verify transformer extracts normalized, deduplicated categories and competitions."""
    transformer = CompetitionsTransformer()
    categories, competitions = transformer.transform(sample_competitions_payload)

    assert len(categories) > 0
    assert len(competitions) > 0

    # Ensure categories are unique
    cat_ids = [c.category_id for c in categories]
    assert len(cat_ids) == len(set(cat_ids))

    # Check category fields
    cat = categories[0]
    assert cat.category_id.startswith("sr:category:")
    assert len(cat.category_name) > 0

    # Check competition fields
    comp = competitions[0]
    assert comp.competition_id.startswith("sr:competition:")
    assert comp.type in ("singles", "doubles", "mixed")
    assert comp.gender in ("men", "women", "mixed")


def test_transformer_malformed_entry_skipped():
    """Verify transformer gracefully skips corrupted elements without aborting batch."""
    corrupted_payload = {
        "competitions": [
            {"id": "sr:comp:valid1", "name": "Valid 1", "category": {"id": "sr:cat:1", "name": "ATP"}},
            {"id": None, "name": "Missing ID", "category": {"id": "sr:cat:1", "name": "ATP"}},  # invalid
            {"id": "sr:comp:valid2", "name": "Valid 2", "category": {"id": "sr:cat:1", "name": "ATP"}},
        ]
    }
    transformer = CompetitionsTransformer()
    categories, competitions = transformer.transform(corrupted_payload)

    assert len(competitions) == 2
    assert competitions[0].competition_id == "sr:comp:valid1"
    assert competitions[1].competition_id == "sr:comp:valid2"
