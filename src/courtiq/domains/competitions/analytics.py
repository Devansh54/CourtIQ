"""CourtIQ Competitions Analytics Service.

Provides domain metrics, distribution aggregations, and Plotly visualization
generators for competitions and categories.
"""

from typing import Any, Dict, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from courtiq.domains.competitions.repository import CompetitionsRepository


class CompetitionsAnalytics:
    """Analytics and visualization generator for the Competitions domain."""

    def __init__(self, repository: Optional[CompetitionsRepository] = None) -> None:
        """Initialize CompetitionsAnalytics.

        Args:
            repository: CompetitionsRepository instance.
        """
        self.repo = repository or CompetitionsRepository()

    def get_summary_kpis(self) -> Dict[str, Any]:
        """Compute high-level KPIs for the Competitions domain."""
        total_comps = self.repo.get_competition_count()
        total_cats = self.repo.get_category_count()

        df_all = self.repo.query_1_all_with_category()
        if df_all.empty:
            return {
                "total_competitions": 0,
                "total_categories": 0,
                "doubles_count": 0,
                "singles_count": 0,
                "parent_competitions": 0,
                "sub_competitions": 0,
            }

        doubles_count = len(df_all[df_all["type"].str.lower() == "doubles"])
        singles_count = len(df_all[df_all["type"].str.lower() == "singles"])
        sub_count = len(df_all[df_all["parent_id"].notna() & (df_all["parent_id"] != "")])
        parent_count = total_comps - sub_count

        return {
            "total_competitions": total_comps,
            "total_categories": total_cats,
            "doubles_count": doubles_count,
            "singles_count": singles_count,
            "parent_competitions": parent_count,
            "sub_competitions": sub_count,
        }

    def create_category_bar_chart(self) -> go.Figure:
        """Generate Plotly horizontal bar chart of competition count by category."""
        df = self.repo.query_2_count_by_category()
        if df.empty:
            fig = go.Figure()
            fig.update_layout(title="No Category Data Available")
            return fig

        fig = px.bar(
            df,
            x="competition_count",
            y="category_name",
            orientation="h",
            text="competition_count",
            color="competition_count",
            color_continuous_scale="Blues",
            labels={"competition_count": "Total Competitions", "category_name": "Category"},
            title="Competitions Distribution Across Categories",
        )
        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=20, r=20, t=40, b=20),
            coloraxis_showscale=False,
            height=320,
        )
        return fig

    def create_type_sunburst_or_pie(self) -> go.Figure:
        """Generate Plotly Donut chart for competition formats (singles vs. doubles)."""
        df = self.repo.query_1_all_with_category()
        if df.empty:
            fig = go.Figure()
            fig.update_layout(title="No Competition Format Data")
            return fig

        type_counts = df["type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]

        fig = px.pie(
            type_counts,
            names="type",
            values="count",
            hole=0.45,
            color="type",
            color_discrete_map={"doubles": "#26A69A", "singles": "#1E88E5", "mixed": "#FFA726"},
            title="Event Formats (Singles vs. Doubles)",
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=320)
        return fig

    def create_type_distribution_stacked_bar(self) -> go.Figure:
        """Generate stacked bar chart of competition formats by category."""
        df = self.repo.query_6_type_distribution_by_category()
        if df.empty:
            fig = go.Figure()
            fig.update_layout(title="No Type Distribution Data")
            return fig

        fig = px.bar(
            df,
            x="category_name",
            y="competition_count",
            color="type",
            barmode="stack",
            color_discrete_map={"doubles": "#26A69A", "singles": "#1E88E5", "mixed": "#FFA726"},
            labels={"competition_count": "Count", "category_name": "Category", "type": "Type"},
            title="Distribution of Competition Formats by Category",
        )
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=340)
        return fig
