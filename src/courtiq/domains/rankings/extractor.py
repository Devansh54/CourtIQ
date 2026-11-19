"""CourtIQ Rankings Extractor.

Domain Owner: Rankings & Analytics Module Owner (25% Contribution)
Reference: docs/handoffs/RANKINGS_MODULE_HANDOFF.md
"""

from typing import Any, Dict, Optional

from courtiq.core.api_client import SportradarClient
from courtiq.core.exceptions import APIError


class RankingsExtractor:
    """Extract doubles competitor rankings from Sportradar."""

    ENDPOINT = "double_competitor_rankings.json"

    def __init__(
        self,
        api_client: Optional[SportradarClient] = None
    ) -> None:
        self.client = api_client or SportradarClient()

    def extract(self) -> Dict[str, Any]:
        """Fetch and validate the raw doubles rankings payload."""

        payload = self.client.get(self.ENDPOINT)

        if not isinstance(payload, dict):
            raise APIError("Invalid rankings API response: expected a dictionary.")

        if "rankings" not in payload:
            raise APIError("Invalid rankings API response: missing 'rankings'.")

        if not isinstance(payload["rankings"], list):
            raise APIError("Invalid rankings API response: 'rankings' must be a list.")

        for collection in payload["rankings"]:
            if not isinstance(collection, dict):
                raise APIError("Invalid rankings collection: expected a dictionary.")

            if not isinstance(collection.get("competitor_rankings"), list):
                raise APIError(
                    "Invalid rankings collection: missing or invalid "
                    "'competitor_rankings' list."
                )

        return payload