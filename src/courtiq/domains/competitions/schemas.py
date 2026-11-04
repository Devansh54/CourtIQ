"""CourtIQ Competitions Domain Schemas.

Pydantic data models enforcing strict type validation and structural contracts
for tennis categories, competitions, and hierarchy structures.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CategoryBase(BaseModel):
    """Base schema for category attributes."""
    category_id: str = Field(..., min_length=1, max_length=50, description="Sportradar category ID (e.g. sr:category:1)")
    category_name: str = Field(..., min_length=1, max_length=100, description="Display name of category")

    @field_validator("category_id", "category_name")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class Category(CategoryBase):
    """Represents a validated category entity stored in the database."""
    pass


class CompetitionBase(BaseModel):
    """Base schema for competition attributes."""
    competition_id: str = Field(..., min_length=1, max_length=50, description="Sportradar competition ID")
    competition_name: str = Field(..., min_length=1, max_length=100, description="Name of competition")
    parent_id: Optional[str] = Field(default=None, max_length=50, description="Parent competition ID if sub-competition")
    type: str = Field(..., min_length=1, max_length=20, description="Format (singles, doubles, mixed)")
    gender: str = Field(..., min_length=1, max_length=10, description="Gender (men, women, mixed)")
    category_id: str = Field(..., min_length=1, max_length=50, description="Foreign key to categories table")

    @field_validator("competition_id", "competition_name", "type", "gender", "category_id")
    @classmethod
    def clean_strings(cls, v: str) -> str:
        return v.strip()

    @field_validator("parent_id")
    @classmethod
    def clean_parent_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            return cleaned if cleaned else None
        return None


class Competition(CompetitionBase):
    """Represents a validated competition entity stored in the database."""
    pass


class CompetitionWithCategory(BaseModel):
    """Enriched competition entity with joined category name."""
    competition_id: str
    competition_name: str
    parent_id: Optional[str] = None
    type: str
    gender: str
    category_id: str
    category_name: str


class ParentSubHierarchy(BaseModel):
    """Represents a parent competition and its associated sub-competition."""
    parent_id: str
    parent_name: str
    sub_competition_id: str
    sub_competition_name: str
    type: str
    gender: str
