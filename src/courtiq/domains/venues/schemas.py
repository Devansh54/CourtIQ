
"""CourtIQ Complexes & Venues Domain Schemas."""

from pydantic import BaseModel, Field, field_validator


class ComplexBase(BaseModel):
    """Base schema for sports complex entity."""

    complex_id: str = Field(..., min_length=1, max_length=50)
    complex_name: str = Field(..., min_length=1, max_length=100)

    @field_validator("complex_id", "complex_name")
    @classmethod
    def clean_strings(cls, v: str) -> str:
        return v.strip()


class Complex(ComplexBase):
    """Validated sports complex entity."""
    pass


class VenueBase(BaseModel):
    """Base schema for sports venue entity."""

    venue_id: str = Field(..., min_length=1, max_length=50)
    venue_name: str = Field(..., min_length=1, max_length=100)
    city_name: str = Field(..., min_length=1, max_length=100)
    country_name: str = Field(..., min_length=1, max_length=100)
    country_code: str = Field(..., min_length=2, max_length=3)
    timezone: str = Field(..., min_length=1, max_length=100)
    complex_id: str = Field(..., min_length=1, max_length=50)

    @field_validator(
        "venue_id",
        "venue_name",
        "city_name",
        "country_name",
        "timezone",
        "complex_id",
    )
    @classmethod
    def clean_strings(cls, v: str) -> str:
        return v.strip()

    @field_validator("country_code", mode="before")
    @classmethod
    def clean_country_code(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().upper()
        return v


class Venue(VenueBase):
    """Validated sports venue entity."""
    pass
