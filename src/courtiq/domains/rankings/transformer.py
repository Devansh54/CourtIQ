"""CourtIQ Rankings Transformer.

Domain Owner: Rankings & Analytics Module Owner (25% Contribution)
"""

from typing import Any, Dict, List, Tuple

from pydantic import ValidationError

from courtiq.core.exceptions import TransformationError
from courtiq.domains.rankings.schemas import Competitor, CompetitorRanking


class RankingsTransformer:
    """Transform raw rankings JSON into validated Python objects."""

    def transform(
        self,
        raw_payload: Dict[str, Any]
    ) -> Tuple[List[Competitor], List[CompetitorRanking]]:
        """Convert rankings payload into competitor and ranking objects."""

        if not isinstance(raw_payload, dict):
            raise TransformationError("Rankings payload must be a dictionary.")

        collections = raw_payload.get("rankings")

        if not isinstance(collections, list):
            raise TransformationError(
                "Rankings payload must contain a rankings list."
            )

        competitors: Dict[str, Competitor] = {}
        rankings: List[CompetitorRanking] = []

        try:
            for collection in collections:
                if not isinstance(collection, dict):
                    raise TransformationError(
                        "Each ranking collection must be a dictionary."
                    )

                records = collection.get("competitor_rankings")

                if not isinstance(records, list):
                    raise TransformationError(
                        "Each collection must contain competitor_rankings."
                    )

                for record in records:
                    if not isinstance(record, dict):
                        raise TransformationError(
                            "Each competitor ranking must be a dictionary."
                        )

                    competitor_data = record.get("competitor")

                    if not isinstance(competitor_data, dict):
                        raise TransformationError(
                            "Ranking record is missing competitor details."
                        )

                    competitor = Competitor(
                        competitor_id=competitor_data["id"],
                        name=competitor_data["name"],
                        country=competitor_data["country"],
                        country_code=competitor_data["country_code"],
                        abbreviation=competitor_data["abbreviation"],
                    )

                    competitor_id = competitor.competitor_id
                    competitors[competitor_id] = competitor

                    ranking = CompetitorRanking(
                        rank=record["rank"],
                        movement=record["movement"],
                        points=record["points"],
                        competitions_played=record["competitions_played"],
                        competitor_id=competitor_id,
                    )

                    rankings.append(ranking)

        except (KeyError, TypeError, ValidationError) as exc:
            raise TransformationError(
                f"Failed to transform rankings data: {exc}"
            ) from exc

        return list(competitors.values()), rankings