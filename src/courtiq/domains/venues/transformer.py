"""CourtIQ Venues Transformer."""

from typing import Any, Dict, List, Tuple

from pydantic import ValidationError

from courtiq.core.exceptions import TransformationError
from courtiq.domains.venues.schemas import Complex, Venue


class VenuesTransformer:
    """Transform raw complexes JSON into validated records."""

    def transform(
        self,
        raw_payload: Dict[str, Any]
    ) -> Tuple[List[Complex], List[Venue]]:

        if not isinstance(raw_payload, dict):
            raise TransformationError("Payload must be a dictionary.")

        complexes_data = raw_payload.get("complexes")

        if not isinstance(complexes_data, list):
            raise TransformationError(
                "'complexes' must be a list."
            )

        complexes: List[Complex] = []
        venues: List[Venue] = []

        try:
            for complex_data in complexes_data:
                if not isinstance(complex_data, dict):
                    raise TransformationError("Invalid complex record.")

                complex_obj = Complex(
                    complex_id=complex_data.get("id"),
                    complex_name=complex_data.get("name")
                )
                complexes.append(complex_obj)

                venues_data = complex_data.get("venues", [])

                if not isinstance(venues_data, list):
                    raise TransformationError(
                        f"Venues must be a list for {complex_obj.complex_id}."
                    )

                for venue_data in venues_data:
                    if not isinstance(venue_data, dict):
                        raise TransformationError("Invalid venue record.")

                    venue_obj = Venue(
                        venue_id=venue_data.get("id"),
                        venue_name=venue_data.get("name"),
                        city_name=venue_data.get("city_name"),
                        country_name=venue_data.get("country_name"),
                        country_code=venue_data.get("country_code"),
                        timezone=venue_data.get("timezone"),
                        complex_id=complex_obj.complex_id
                    )
                    venues.append(venue_obj)

        except ValidationError as exc:
            raise TransformationError(
                f"Venue data validation failed: {exc}"
            ) from exc

        return complexes, venues
