"""CourtIQ Rankings Repository.

Domain Owner: Rankings & Analytics Module Owner (25% Contribution)
"""

from pathlib import Path
from typing import List, Optional

import pandas as pd

from courtiq.core.database import DatabaseManager, get_db
from courtiq.domains.rankings.schemas import Competitor, CompetitorRanking
from sqlalchemy import text

class RankingsRepository:
    """Repository managing SQL persistence and analytics for competitors and rankings."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None) -> None:
        self.db = db_manager or get_db()
        self.query_dir = (
            Path(__file__).resolve().parents[4]
            / "sql"
            / "queries"
            / "rankings"
        )

    def _read_query(self, filename: str) -> str:
        """Read a SQL query file."""
        query_path = self.query_dir / filename

        if not query_path.exists():
            raise FileNotFoundError(f"SQL query file not found: {query_path}")

        return query_path.read_text(encoding="utf-8-sig")

    def save_competitors(self, competitors: List[Competitor]) -> int:
        """Insert or update competitors without creating duplicates."""
        if not competitors:
            return 0

        query = """
            INSERT INTO competitors (
                competitor_id,
                name,
                country,
                country_code,
                abbreviation
            )
            VALUES (
                :competitor_id,
                :name,
                :country,
                :country_code,
                :abbreviation
            )
            ON CONFLICT (competitor_id)
            DO UPDATE SET
                name = EXCLUDED.name,
                country = EXCLUDED.country,
                country_code = EXCLUDED.country_code,
                abbreviation = EXCLUDED.abbreviation;
        """

        records = [competitor.model_dump() for competitor in competitors]
        self.db.execute_many(query, records)

        return len(records)

    def save_rankings(self, rankings: List[CompetitorRanking]) -> int:
        """Replace the current rankings snapshot in one transaction."""
        if not rankings:
            return 0

        records = [
            ranking.model_dump(exclude={"rank_id"})
            for ranking in rankings
        ]

        with self.db.transaction() as connection:
            connection.execute(text("DELETE FROM competitor_rankings"))

            insert_query = """
                INSERT INTO competitor_rankings (
                    rank,
                    movement,
                    points,
                    competitions_played,
                    competitor_id
                )
                VALUES (
                    :rank,
                    :movement,
                    :points,
                    :competitions_played,
                    :competitor_id
                );
            """

            connection.execute(text(insert_query), records)

        return len(records)

    def get_competitor_count(self) -> int:
        """Return the number of stored competitors."""
        result = self.db.fetch_one(
            "SELECT COUNT(*) AS total FROM competitors"
        )
        return int(result["total"]) if result else 0

    def get_rankings_count(self) -> int:
        """Return the number of stored ranking records."""
        result = self.db.fetch_one(
            "SELECT COUNT(*) AS total FROM competitor_rankings"
        )
        return int(result["total"]) if result else 0

    def query_1_competitors_rank_points(self) -> pd.DataFrame:
        """Return the top-ranked competitors."""
        return self.db.fetch_df(
            self._read_query("q1_top_ranked_competitors.sql")
        )

    def query_2_top_5_competitors(self) -> pd.DataFrame:
        """Return the top five competitors."""
        query = self._read_query("q1_top_ranked_competitors.sql")
        query = query.replace("LIMIT 10", "LIMIT 5")
        return self.db.fetch_df(query)

    def query_3_stable_rank_competitors(self) -> pd.DataFrame:
        """Return competitors whose ranking movement is zero."""
        return self.db.fetch_df(
            self._read_query(
                "q5_unranked_or_zero_movement_competitors.sql"
            )
        )

    def query_4_points_by_country(
        self, country: str = "Croatia"
    ) -> pd.DataFrame:
        """Return rankings for competitors from a selected country."""
        query = self._read_query("q2_rankings_by_country.sql")
        return self.db.fetch_df(
            query,
            params={"country_name": country}
        )

    def query_5_competitors_per_country(self) -> pd.DataFrame:
        """Return competitor counts grouped by country."""
        query = """
            SELECT
                country,
                country_code,
                COUNT(*) AS total_competitors
            FROM competitors
            GROUP BY country, country_code
            ORDER BY total_competitors DESC, country ASC;
        """
        return self.db.fetch_df(query)

    def query_6_highest_points_competitors(self) -> pd.DataFrame:
        """Return competitors ordered by points, highest first."""
        query = """
            SELECT
                c.competitor_id,
                c.name,
                c.country,
                cr.rank,
                cr.points,
                cr.movement,
                cr.competitions_played
            FROM competitor_rankings cr
            JOIN competitors c
                ON cr.competitor_id = c.competitor_id
            ORDER BY cr.points DESC, cr.rank ASC
            LIMIT 10;
        """
        return self.db.fetch_df(query)