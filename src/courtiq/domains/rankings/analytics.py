"""CourtIQ Rankings Analytics.

Domain Owner: Rankings & Analytics Module Owner
"""

from typing import Any, Dict, Optional

import plotly.express as px
import plotly.graph_objects as go

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

    def create_top_competitors_chart(self, limit: int = 10) -> go.Figure:
        """Create horizontal bar chart of top competitors by ranking points."""
        df = self.repo.query_1_top_ranked_competitors()
        if df.empty:
            return go.Figure()
        df_top = df.head(limit).sort_values("points", ascending=True)
        fig = px.bar(
            df_top,
            x="points",
            y="name",
            orientation="h",
            title=f"Top {limit} Doubles Competitors by Points",
            labels={"points": "Ranking Points", "name": "Competitor"},
            text="points",
            template="plotly_white",
        )
        return fig

    def create_competitions_vs_points_scatter(self) -> go.Figure:
        """Create scatter plot correlating competitions played vs. ranking points."""
        df = self.repo.query_4_competitions_played_vs_points()
        if df.empty:
            return go.Figure()
        fig = px.scatter(
            df,
            x="competitions_played",
            y="points",
            hover_name="name",
            color="country",
            title="Competitions Played vs. Ranking Points",
            labels={
                "competitions_played": "Competitions Played",
                "points": "Ranking Points",
                "country": "Country",
            },
            template="plotly_white",
        )
        return fig

    def create_country_points_pie(self) -> go.Figure:
        """Create donut chart showing ranking points distribution by country."""
        df = self.repo.query_6_points_distribution_by_country()
        if df.empty:
            return go.Figure()
        fig = px.pie(
            df,
            names="country",
            values="total_points",
            hole=0.4,
            title="Ranking Points Share by Country",
            template="plotly_white",
        )
        return fig

    def create_country_competitors_bar(self) -> go.Figure:
        """Create bar chart showing competitor count by country."""
        df = self.repo.query_5_competitors_per_country()
        if df.empty:
            return go.Figure()
        fig = px.bar(
            df,
            x="country",
            y="total_competitors",
            text="total_competitors",
            title="Competitors Count by Country",
            labels={"country": "Country", "total_competitors": "Competitors"},
            template="plotly_white",
        )
        return fig