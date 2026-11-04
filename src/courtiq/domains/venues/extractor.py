"""CourtIQ Venues API Extractor Interface Contract.

Domain Owner: Venue & Complexes Module Owner (25% Contribution)
Reference: docs/handoffs/VENUES_MODULE_HANDOFF.md
"""

from typing import Any, Dict, Optional
from courtiq.core.api_client import SportradarClient


class VenuesExtractor:
    """Extractor contract for Sportradar complexes & venues endpoint.

    To be implemented by Venue & Complexes Module Owner.
    """

    ENDPOINT = "complexes.json"

    def __init__(self, api_client: Optional[SportradarClient] = None) -> None:
        self.client = api_client or SportradarClient()

    def extract(self) -> Dict[str, Any]:
        """Fetch raw complexes payload.

        Implemented by Venue & Complexes Module Owner.
        """
        raise NotImplementedError(
            "VenuesExtractor is assigned to the Venue & Complexes Module Owner. "
            "See docs/handoffs/VENUES_MODULE_HANDOFF.md for implementation instructions."
        )
