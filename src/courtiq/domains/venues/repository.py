"""CourtIQ Venues Repository Interface Contract.

Domain Owner: Venue & Complexes Module Owner (25% Contribution)
Reference: docs/handoffs/VENUES_MODULE_HANDOFF.md
"""

from typing import List, Optional
import pandas as pd
from courtiq.core.database import DatabaseManager, get_db
from courtiq.domains.venues.schemas import Complex, Venue


class VenuesRepository:
    """Repository managing SQL persistence and analytics for complexes and venues.

    To be implemented by Venue & Complexes Module Owner.
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None) -> None:
        self.db = db_manager or get_db()

    def save_complexes(self, complexes: List[Complex]) -> int:
        raise NotImplementedError("Assigned to Venue & Complexes Module Owner.")

    def save_venues(self, venues: List[Venue]) -> int:
        raise NotImplementedError("Assigned to Venue & Complexes Module Owner.")

    def query_1_venues_with_complex(self) -> pd.DataFrame:
        raise NotImplementedError("Assigned to Venue & Complexes Module Owner.")

    def query_2_venues_count_per_complex(self) -> pd.DataFrame:
        raise NotImplementedError("Assigned to Venue & Complexes Module Owner.")

    def query_3_venues_by_country(self, country: str = "Chile") -> pd.DataFrame:
        raise NotImplementedError("Assigned to Venue & Complexes Module Owner.")

    def query_4_venues_and_timezones(self) -> pd.DataFrame:
        raise NotImplementedError("Assigned to Venue & Complexes Module Owner.")

    def query_5_multi_venue_complexes(self) -> pd.DataFrame:
        raise NotImplementedError("Assigned to Venue & Complexes Module Owner.")

    def query_6_venues_by_country_group(self) -> pd.DataFrame:
        raise NotImplementedError("Assigned to Venue & Complexes Module Owner.")

    def query_7_venues_for_specific_complex(self, complex_name: str = "Nacional") -> pd.DataFrame:
        raise NotImplementedError("Assigned to Venue & Complexes Module Owner.")
