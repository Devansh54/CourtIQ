"""CourtIQ Venues Analytics Interface Contract.

Domain Owner: Venue & Complexes Module Owner (25% Contribution)
Reference: docs/handoffs/VENUES_MODULE_HANDOFF.md
"""

from typing import Any, Dict, Optional
from courtiq.domains.venues.repository import VenuesRepository


class VenuesAnalytics:
    """Analytics and visualizations for the Complexes & Venues domain.

    To be implemented by Venue & Complexes Module Owner.
    """

    def __init__(self, repository: Optional[VenuesRepository] = None) -> None:
        self.repo = repository or VenuesRepository()

    def get_summary_kpis(self) -> Dict[str, Any]:
        raise NotImplementedError("Assigned to Venue & Complexes Module Owner.")
