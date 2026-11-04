"""CourtIQ Doubles Competitor Rankings Domain Schemas.

Domain Owner: Rankings & Analytics Module Owner (25% Contribution)
Reference: REQ-RNK-03, REQ-RNK-04 (PDF Pages 6-7)
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CompetitorBase(BaseModel):
    """Base schema for competitor entity."""
    competitor_id: str = Field(..., min_length=1, max_length=50, description="Sportradar competitor ID (e.g. sr:competitor:101)")
    name: str = Field(..., min_length=1, max_length=100, description="Full name of competitor")
    country: str = Field(..., min_length=1, max_length=100, description="Competitor's country")
    country_code: str = Field(..., min_length=2, max_length=3, description="ISO 3166-1 alpha-3 nationality code")
    abbreviation: str = Field(..., min_length=1, max_length=10, description="Shortened player abbreviation")

    @field_validator("competitor_id", "name", "country", "abbreviation")
    @classmethod
    def clean_strings(cls, v: str) -> str:
        return v.strip()

    @field_validator("country_code")
    @classmethod
    def clean_country_code(cls, v: str) -> str:
        return v.strip().upper()


class Competitor(CompetitorBase):
    """Validated competitor entity."""
    pass


class CompetitorRankingBase(BaseModel):
    """Base schema for ranking record."""
    rank_id: Optional[int] = Field(default=None, description="Surrogate primary key auto-incremented")
    rank: int = Field(..., ge=1, description="Official doubles ranking position")
    movement: int = Field(..., description="Week-over-week movement")
    points: int = Field(..., ge=0, description="Accumulated ranking points")
    competitions_played: int = Field(..., ge=0, description="Number of competitions played")
    competitor_id: str = Field(..., min_length=1, max_length=50, description="Foreign key to competitors table")


class CompetitorRanking(CompetitorRankingBase):
    """Validated ranking record entity."""
    pass
