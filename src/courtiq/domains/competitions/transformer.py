"""CourtIQ Competitions Data Transformer.

Transforms nested Sportradar competitions JSON responses into normalized,
validated relational Category and Competition entities.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import ValidationError

from courtiq.core.exceptions import TransformationError
from courtiq.core.logging_config import get_logger
from courtiq.domains.competitions.schemas import Category, Competition

logger = get_logger("domains.competitions.transformer")


class CompetitionsTransformer:
    """Transforms raw competitions JSON payloads into normalized relational entities."""

    def transform(self, raw_payload: Dict[str, Any]) -> Tuple[List[Category], List[Competition]]:
        """Normalize raw competitions JSON into validated Category and Competition objects.

        Args:
            raw_payload: Dictionary parsed from Sportradar competitions endpoint.

        Returns:
            Tuple of (unique categories list, competitions list).

        Raises:
            TransformationError: If the payload cannot be parsed.
        """
        raw_competitions = raw_payload.get("competitions", [])
        if not isinstance(raw_competitions, list):
            raise TransformationError("Expected 'competitions' to be a list in API payload.")

        categories_by_id: Dict[str, Category] = {}
        competitions: List[Competition] = []
        validation_errors_count = 0

        for idx, item in enumerate(raw_competitions):
            try:
                # 1. Parse and extract Category entity
                raw_cat = item.get("category")
                if not raw_cat or not isinstance(raw_cat, dict):
                    # Handle competitions that might lack explicit category dictionary
                    cat_id = item.get("category_id", "sr:category:default")
                    cat_name = item.get("category_name", "General Tennis")
                else:
                    cat_id = raw_cat.get("id") or item.get("category_id")
                    cat_name = raw_cat.get("name") or "Unclassified"

                if not cat_id:
                    logger.warning("Item index %d missing category id. Skipping.", idx)
                    continue

                if cat_id not in categories_by_id:
                    category_model = Category(
                        category_id=str(cat_id),
                        category_name=str(cat_name),
                    )
                    categories_by_id[cat_id] = category_model

                # 2. Parse and extract Competition entity
                comp_id = item.get("id") or item.get("competition_id")
                comp_name = item.get("name") or item.get("competition_name")
                parent_id = item.get("parent_id")
                comp_type = item.get("type", "singles")
                gender = item.get("gender", "men")

                if not comp_id or not comp_name:
                    logger.warning("Item index %d missing competition id or name. Skipping.", idx)
                    continue

                competition_model = Competition(
                    competition_id=str(comp_id),
                    competition_name=str(comp_name),
                    parent_id=str(parent_id) if parent_id else None,
                    type=str(comp_type),
                    gender=str(gender),
                    category_id=str(cat_id),
                )
                competitions.append(competition_model)

            except ValidationError as ve:
                validation_errors_count += 1
                logger.warning("Validation error on competition item %d: %s", idx, ve)
                continue
            except Exception as ex:
                validation_errors_count += 1
                logger.warning("Unexpected error transforming item %d: %s", idx, ex)
                continue

        logger.info(
            "Transformation completed: %d unique categories, %d competitions extracted (%d errors skipped).",
            len(categories_by_id),
            len(competitions),
            validation_errors_count,
        )

        return list(categories_by_id.values()), competitions
