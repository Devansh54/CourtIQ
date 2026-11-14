"""CourtIQ Venues Repository."""

from typing import List, Optional

import pandas as pd

from courtiq.core.config import get_settings
from courtiq.core.database import DatabaseManager, get_db
from courtiq.domains.venues.schemas import Complex, Venue


class VenuesRepository:
    """Database repository for complexes and venues."""

    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None
    ) -> None:
        self.db = db_manager or get_db()
        self.queries_dir = (
            get_settings().project_root
            / "sql"
            / "queries"
            / "venues"
        )

    def _read_query(self, filename: str) -> str:
        path = self.queries_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"SQL file not found: {path}")
        return path.read_text(encoding="utf-8")

    def save_complexes(self, complexes: List[Complex]) -> int:
        if not complexes:
            return 0

        query = """
            INSERT INTO complexes (complex_id, complex_name)
            VALUES (:complex_id, :complex_name)
            ON CONFLICT (complex_id) DO UPDATE SET
                complex_name = EXCLUDED.complex_name;
        """
        params = [
            {
                "complex_id": c.complex_id,
                "complex_name": c.complex_name,
            }
            for c in complexes
        ]
        return self.db.execute_many(query, params)

    def save_venues(self, venues: List[Venue]) -> int:
        if not venues:
            return 0

        query = """
            INSERT INTO venues (
                venue_id, venue_name, city_name, country_name,
                country_code, timezone, complex_id
            )
            VALUES (
                :venue_id, :venue_name, :city_name, :country_name,
                :country_code, :timezone, :complex_id
            )
            ON CONFLICT (venue_id) DO UPDATE SET
                venue_name = EXCLUDED.venue_name,
                city_name = EXCLUDED.city_name,
                country_name = EXCLUDED.country_name,
                country_code = EXCLUDED.country_code,
                timezone = EXCLUDED.timezone,
                complex_id = EXCLUDED.complex_id;
        """
        params = [
            {
                "venue_id": v.venue_id,
                "venue_name": v.venue_name,
                "city_name": v.city_name,
                "country_name": v.country_name,
                "country_code": v.country_code,
                "timezone": v.timezone,
                "complex_id": v.complex_id,
            }
            for v in venues
        ]
        return self.db.execute_many(query, params)

    def get_complex_count(self) -> int:
        result = self.db.fetch_one(
            "SELECT COUNT(*) AS count FROM complexes;"
        )
        return int(result["count"]) if result else 0

    def get_venue_count(self) -> int:
        result = self.db.fetch_one(
            "SELECT COUNT(*) AS count FROM venues;"
        )
        return int(result["count"]) if result else 0

    def query_1_venues_with_complex(self) -> pd.DataFrame:
        return self.db.fetch_df(
            self._read_query("q1_venues_with_complex.sql")
        )

    def query_2_venues_count_per_complex(self) -> pd.DataFrame:
        return self.db.fetch_df(
            self._read_query("q2_venues_count_per_complex.sql")
        )

    def query_3_venues_by_country(
        self, country: str = "Chile"
    ) -> pd.DataFrame:
        return self.db.fetch_df(
            self._read_query("q3_venues_by_country.sql"),
            params={"country_name": country},
        )

    def query_4_venues_and_timezones(self) -> pd.DataFrame:
        return self.db.fetch_df(
            self._read_query("q4_venues_and_timezones.sql")
        )

    def query_5_multi_venue_complexes(self) -> pd.DataFrame:
        return self.db.fetch_df(
            self._read_query("q5_multi_venue_complexes.sql")
        )

    def query_6_venues_by_country_group(self) -> pd.DataFrame:
        return self.db.fetch_df(
            self._read_query("q6_venues_by_country_group.sql")
        )

    def query_7_venues_for_specific_complex(
        self, complex_name: str = "Nacional"
    ) -> pd.DataFrame:
        return self.db.fetch_df(
            self._read_query("q7_venues_for_specific_complex.sql"),
            params={
                "complex_pattern": f"%{complex_name.strip()}%"
            },
        )
