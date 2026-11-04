"""CourtIQ Rankings Transformer Interface Contract.

Domain Owner: Rankings & Analytics Module Owner (25% Contribution)
"""

from typing import Any, Dict, List, Tuple
from courtiq.domains.rankings.schemas import Competitor, CompetitorRanking


class RankingsTransformer:
    """Transforms raw rankings JSON into normalized Competitor and CompetitorRanking entities."""

    def transform(self, raw_payload: Dict[str, Any]) -> Tuple[List[Competitor], List[CompetitorRanking]]:
        raise NotImplementedError(
            "RankingsTransformer is assigned to the Rankings & Analytics Module Owner."
        )
