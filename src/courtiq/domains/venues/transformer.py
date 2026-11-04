"""CourtIQ Venues Transformer Interface Contract.

Domain Owner: Venue & Complexes Module Owner (25% Contribution)
Reference: docs/handoffs/VENUES_MODULE_HANDOFF.md
"""

from typing import Any, Dict, List, Tuple
from courtiq.domains.venues.schemas import Complex, Venue


class VenuesTransformer:
    """Transforms raw complexes JSON payloads into normalized Complex and Venue entities.

    To be implemented by Venue & Complexes Module Owner.
    """

    def transform(self, raw_payload: Dict[str, Any]) -> Tuple[List[Complex], List[Venue]]:
        """Normalize raw JSON into validated Complex and Venue objects.

        Implemented by Venue & Complexes Module Owner.
        """
        raise NotImplementedError(
            "VenuesTransformer is assigned to the Venue & Complexes Module Owner. "
            "See docs/handoffs/VENUES_MODULE_HANDOFF.md for implementation instructions."
        )
