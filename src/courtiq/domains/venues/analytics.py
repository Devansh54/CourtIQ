"""CourtIQ Venues Analytics Service."""

from typing import Any, Dict, Optional

import plotly.express as px
import plotly.graph_objects as go

from courtiq.domains.venues.repository import VenuesRepository


class VenuesAnalytics:
    """Analytics for complexes and venues."""

    def __init__(self, repository: Optional[VenuesRepository] = None):
        self.repo = repository or VenuesRepository()

    def get_summary_kpis(self) -> Dict[str, Any]:
        total_complexes = self.repo.get_complex_count()
        total_venues = self.repo.get_venue_count()
        venues = self.repo.query_1_venues_with_complex()
        countries = self.repo.query_6_venues_by_country_group()

        return {
            "total_complexes": total_complexes,
            "total_venues": total_venues,
            "total_countries": int(countries["country_code"].nunique()) if not countries.empty else 0,
            "total_cities": int(venues["city_name"].nunique()) if not venues.empty else 0,
            "average_venues_per_complex": round(total_venues / total_complexes, 2) if total_complexes else 0,
        }

    def create_country_bar_chart(self) -> go.Figure:
        df = self.repo.query_6_venues_by_country_group()
        if df.empty:
            return go.Figure()
        return px.bar(df, x="country_name", y="total_venues", text="total_venues", title="Venues by Country", template="plotly_white")

    def create_complex_bar_chart(self) -> go.Figure:
        df = self.repo.query_2_venues_count_per_complex()
        if df.empty:
            return go.Figure()
        return px.bar(df, x="complex_name", y="total_venues", text="total_venues", title="Venues per Complex", template="plotly_white")

    def create_timezone_pie_chart(self) -> go.Figure:
        df = self.repo.query_4_venues_and_timezones()
        if df.empty:
            return go.Figure()
        counts = df["timezone"].value_counts().rename_axis("timezone").reset_index(name="venue_count")
        return px.pie(counts, names="timezone", values="venue_count", hole=0.4, title="Venues by Timezone", template="plotly_white")
