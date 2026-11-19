"""CourtIQ Rankings Analytics.

Domain Owner: Rankings & Analytics Module Owner (25% Contribution)
"""

from typing import Any, Dict, Optional

from courtiq.core.database import DatabaseManager
from courtiq.domains.rankings.repository import RankingsRepository


class RankingsAnalytics:
    """Analytics for the Doubles Competitor Rankings domain."""

    def __init__(
        self,
        repository: Optional[RankingsRepository] = None
    ) -> None:
        self.repo = repository or RankingsRepository()

    def get_summary_kpis(self) -> Dict[str, Any]:
        """Calculate summary KPIs for the rankings dashboard."""

        query = """
            SELECT
                COUNT(DISTINCT cr.competitor_id) AS total_competitors,
                COUNT(DISTINCT c.country_code) AS total_countries,
                COALESCE(ROUND(AVG(cr.points), 2), 0) AS average_points,

                (
                    SELECT c2.name
                    FROM competitor_rankings cr2
                    JOIN competitors c2
                        ON cr2.competitor_id = c2.competitor_id
                    ORDER BY cr2.rank ASC
                    LIMIT 1
                ) AS top_ranked_competitor,

                (
                    SELECT c3.name
                    FROM competitor_rankings cr3
                    JOIN competitors c3
                        ON cr3.competitor_id = c3.competitor_id
                    WHERE cr3.movement > 0
                    ORDER BY cr3.movement DESC, cr3.rank ASC
                    LIMIT 1
                ) AS biggest_rank_gainer

            FROM competitor_rankings cr
            JOIN competitors c
                ON cr.competitor_id = c.competitor_id;
        """

        result = self.repo.db.fetch_one(query) or {}

        return {
            "total_competitors": int(result.get("total_competitors") or 0),
            "total_countries": int(result.get("total_countries") or 0),
            "average_points": float(result.get("average_points") or 0),
            "top_ranked_competitor": result.get("top_ranked_competitor") or "N/A",
            "biggest_rank_gainer": result.get("biggest_rank_gainer") or "N/A",
        }