"""CourtIQ Complexes & Venues Domain Schemas.

Domain Owner: Venue & Complexes Module Owner (25% Contribution)
Reference: REQ-VEN-03, REQ-VEN-04 (PDF Pages 4-5)
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ComplexBase(BaseModel):
    """Base schema for sports complex entity."""
    complex_id: str = Field(..., min_length=1, max_length=50, description="Sportradar complex ID (e.g. sr:complex:12)")
    complex_name: str = Field(..., min_length=1, max_length=100, description="Name of sports complex")

    @field_validator("complex_id", "complex_name")
    @classmethod
    def clean_strings(cls, v: str) -> str:
        return v.strip()


class Complex(ComplexBase):
    """Validated sports complex entity."""
    pass


class VenueBase(BaseModel):
    """Base schema for sports venue entity."""
    venue_id: str = Field(..., min_length=1, max_length=50, description="Sportradar venue ID (e.g. sr:venue:34)")
    venue_name: str = Field(..., min_length=1, max_length=100, description="Name of the venue or stadium")
    city_name: str = Field(..., min_length=1, max_length=100, description="City where venue is located")
    country_name: str = Field(..., min_length=1, max_length=100, description="Country where venue is located")
    country_code: str = Field(..., min_length=2, max_length=3, description="ISO 3166-1 alpha-3 code")
    timezone: str = Field(..., min_length=1, max_length=100, description="IANA timezone string")
    complex_id: str = Field(..., min_length=1, max_length=50, description="Foreign key referencing complexes table")

    @field_validator("venue_id", "venue_name", "city_name", "country_name", "timezone", "complex_id")
    @classmethod
    def clean_strings(cls, v: str) -> str:
        return v.strip()

    @field_validator("country_code")
    @classmethod
    def clean_country_code(cls, v: str) -> str:
        return v.strip().upper()


class Venue(VenueBase):
    """Validated sports venue entity."""
    pass
