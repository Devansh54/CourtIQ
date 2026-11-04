"""CourtIQ Rankings Repository Interface Contract.

Domain Owner: Rankings & Analytics Module Owner (25% Contribution)
"""

from typing import List, Optional
import pandas as pd
from courtiq.core.database import DatabaseManager, get_db
from courtiq.domains.rankings.schemas import Competitor, CompetitorRanking


class RankingsRepository:
    """Repository managing SQL persistence and analytics for competitors and rankings."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None) -> None:
        self.db = db_manager or get_db()

    def save_competitors(self, competitors: List[Competitor]) -> int:
        raise NotImplementedError("Assigned to Rankings & Analytics Module Owner.")

    def save_rankings(self, rankings: List[CompetitorRanking]) -> int:
        raise NotImplementedError("Assigned to Rankings & Analytics Module Owner.")

    def query_1_competitors_rank_points(self) -> pd.DataFrame:
        raise NotImplementedError("Assigned to Rankings & Analytics Module Owner.")

    def query_2_top_5_competitors(self) -> pd.DataFrame:
        raise NotImplementedError("Assigned to Rankings & Analytics Module Owner.")

    def query_3_stable_rank_competitors(self) -> pd.DataFrame:
        raise NotImplementedError("Assigned to Rankings & Analytics Module Owner.")

    def query_4_points_by_country(self, country: str = "Croatia") -> pd.DataFrame:
        raise NotImplementedError("Assigned to Rankings & Analytics Module Owner.")

    def query_5_competitors_per_country(self) -> pd.DataFrame:
        raise NotImplementedError("Assigned to Rankings & Analytics Module Owner.")

    def query_6_highest_points_competitors(self) -> pd.DataFrame:
        raise NotImplementedError("Assigned to Rankings & Analytics Module Owner.")
