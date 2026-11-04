"""CourtIQ Rankings Extractor Interface Contract.

Domain Owner: Rankings & Analytics Module Owner (25% Contribution)
Reference: docs/handoffs/RANKINGS_MODULE_HANDOFF.md
"""

from typing import Any, Dict, Optional
from courtiq.core.api_client import SportradarClient


class RankingsExtractor:
    """Extractor contract for doubles competitor rankings endpoint."""

    ENDPOINT = "double_competitor_rankings.json"

    def __init__(self, api_client: Optional[SportradarClient] = None) -> None:
        self.client = api_client or SportradarClient()

    def extract(self) -> Dict[str, Any]:
        """Fetch raw doubles competitor rankings payload."""
        raise NotImplementedError(
            "RankingsExtractor is assigned to the Rankings & Analytics Module Owner."
        )
