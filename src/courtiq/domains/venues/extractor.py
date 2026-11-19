
"""CourtIQ Venues API Extractor.

Retrieves raw tennis complexes and venues data from Sportradar.
"""

from typing import Any, Dict, Optional

from courtiq.core.api_client import SportradarClient
from courtiq.core.exceptions import DataValidationError
from courtiq.core.logging_config import get_logger

logger = get_logger("domains.venues.extractor")


class VenuesExtractor:
    """Extractor for Sportradar complexes and venues endpoint."""

    ENDPOINT = "complexes.json"

    def __init__(
        self,
        api_client: Optional[SportradarClient] = None,
    ) -> None:
        """Initialize the Venues extractor."""
        self.client = api_client or SportradarClient()

    def extract(self) -> Dict[str, Any]:
        """Fetch and validate the raw complexes payload.

        Returns:
            Raw JSON dictionary containing complexes and venues.

        Raises:
            DataValidationError: If the API payload is invalid.
        """
        logger.info(
            "Extracting complexes payload from Sportradar endpoint: %s",
            self.ENDPOINT,
        )

        payload = self.client.get(self.ENDPOINT)

        if not isinstance(payload, dict):
            raise DataValidationError(
                "Venues API payload must be a JSON object (dict)."
            )

        if "complexes" not in payload:
            logger.error(
                "API response missing required 'complexes' key."
            )
            raise DataValidationError(
                "Payload missing required 'complexes' collection."
            )

        raw_complexes = payload["complexes"]

        if not isinstance(raw_complexes, list):
            raise DataValidationError(
                "'complexes' collection must be a list."
            )

        logger.info(
            "Successfully extracted %d complex elements.",
            len(raw_complexes),
        )

        return payload
