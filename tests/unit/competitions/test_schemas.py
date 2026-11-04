"""Unit tests for Competitions domain Pydantic schemas."""

import pytest
from pydantic import ValidationError
from courtiq.domains.competitions.schemas import Category, Competition


def test_category_schema_valid():
    """Verify valid Category model creation."""
    cat = Category(category_id="sr:category:1", category_name=" ATP ")
    assert cat.category_id == "sr:category:1"
    assert cat.category_name == "ATP"  # whitespace stripped


def test_category_schema_invalid():
    """Verify Category validation failure on empty fields."""
    with pytest.raises(ValidationError):
        Category(category_id="", category_name="ATP")


def test_competition_schema_valid():
    """Verify valid Competition model creation."""
    comp = Competition(
        competition_id="sr:comp:1",
        competition_name="Australian Open",
        parent_id=None,
        type="singles",
        gender="men",
        category_id="sr:category:1",
    )
    assert comp.competition_name == "Australian Open"
    assert comp.parent_id is None


def test_competition_schema_sub_comp():
    """Verify sub-competition preserves parent_id."""
    comp = Competition(
        competition_id="sr:comp:2",
        competition_name="AO Doubles",
        parent_id="sr:comp:1",
        type="doubles",
        gender="men",
        category_id="sr:category:1",
    )
    assert comp.parent_id == "sr:comp:1"
    assert comp.type == "doubles"
