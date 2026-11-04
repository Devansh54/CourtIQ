"""CourtIQ Competitions API Extractor.

Retrieves raw tennis competition payloads from the Sportradar API.
"""

from typing import Any, Dict, Optional
from courtiq.core.api_client import SportradarClient
from courtiq.core.exceptions import DataValidationError
from courtiq.core.logging_config import get_logger

logger = get_logger("domains.competitions.extractor")


class CompetitionsExtractor:
    """Extractor for Sportradar Tennis competitions endpoint."""

    ENDPOINT = "competitions.json"

    def __init__(self, api_client: Optional[SportradarClient] = None) -> None:
        """Initialize CompetitionsExtractor.

        Args:
            api_client: Configured SportradarClient instance.
        """
        self.client = api_client or SportradarClient()

    def extract(self) -> Dict[str, Any]:
        """Fetch raw competitions payload from Sportradar API or mock fallback.

        Returns:
            Raw dictionary response.

        Raises:
            DataValidationError: If the payload does not contain expected structures.
        """
        logger.info("Extracting competitions payload from Sportradar API endpoint: %s", self.ENDPOINT)
        payload = self.client.get(self.ENDPOINT)

        if not isinstance(payload, dict):
            raise DataValidationError("Competitions API payload must be a JSON object (dict).")

        if "competitions" not in payload:
            logger.error("API response missing required 'competitions' top-level key.")
            raise DataValidationError("Payload missing required 'competitions' collection.")

        raw_comps = payload["competitions"]
        logger.info("Successfully extracted %d raw competition elements.", len(raw_comps))
        return payload
