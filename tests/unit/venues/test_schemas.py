
"""Unit tests for Venues and Complexes Pydantic schemas."""

import pytest
from pydantic import ValidationError

from courtiq.domains.venues.schemas import Complex, Venue


def test_valid_complex():
    complex_obj = Complex(
        complex_id="sr:complex:1",
        complex_name="Melbourne Park"
    )

    assert complex_obj.complex_id == "sr:complex:1"
    assert complex_obj.complex_name == "Melbourne Park"


def test_complex_strings_are_trimmed():
    complex_obj = Complex(
        complex_id=" sr:complex:1 ",
        complex_name=" Melbourne Park "
    )

    assert complex_obj.complex_id == "sr:complex:1"
    assert complex_obj.complex_name == "Melbourne Park"


def test_complex_rejects_empty_name():
    with pytest.raises(ValidationError):
        Complex(
            complex_id="sr:complex:1",
            complex_name=""
        )


def test_valid_venue():
    venue = Venue(
        venue_id="sr:venue:11",
        venue_name="Rod Laver Arena",
        city_name="Melbourne",
        country_name="Australia",
        country_code="aus",
        timezone="Australia/Melbourne",
        complex_id="sr:complex:1"
    )

    assert venue.venue_name == "Rod Laver Arena"
    assert venue.country_code == "AUS"


def test_venue_country_code_is_uppercase():
    venue = Venue(
        venue_id="sr:venue:11",
        venue_name="Rod Laver Arena",
        city_name="Melbourne",
        country_name="Australia",
        country_code="aus",
        timezone="Australia/Melbourne",
        complex_id="sr:complex:1"
    )

    assert venue.country_code == "AUS"


def test_venue_strings_are_trimmed():
    venue = Venue(
        venue_id=" sr:venue:11 ",
        venue_name=" Rod Laver Arena ",
        city_name=" Melbourne ",
        country_name=" Australia ",
        country_code=" aus ",
        timezone=" Australia/Melbourne ",
        complex_id=" sr:complex:1 "
    )

    assert venue.venue_id == "sr:venue:11"
    assert venue.venue_name == "Rod Laver Arena"
    assert venue.city_name == "Melbourne"
    assert venue.country_name == "Australia"
    assert venue.timezone == "Australia/Melbourne"
    assert venue.country_code == "AUS"


def test_venue_rejects_missing_required_field():
    with pytest.raises(ValidationError):
        Venue(
            venue_id="sr:venue:11",
            venue_name="Rod Laver Arena",
            city_name="Melbourne",
            country_name="Australia",
            country_code="AUS",
            timezone="Australia/Melbourne"
        )


def test_venue_rejects_empty_venue_name():
    with pytest.raises(ValidationError):
        Venue(
            venue_id="sr:venue:11",
            venue_name="",
            city_name="Melbourne",
            country_name="Australia",
            country_code="AUS",
            timezone="Australia/Melbourne",
            complex_id="sr:complex:1"
        )
