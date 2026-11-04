"""CourtIQ Data Ingestion Pipeline Runner.

Orchestrates migration execution, API extraction, data transformation,
and idempotent relational database persistence across domains.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from courtiq.core.database import DatabaseManager, get_db
from courtiq.core.logging_config import get_logger
from courtiq.domains.competitions.extractor import CompetitionsExtractor
from courtiq.domains.competitions.transformer import CompetitionsTransformer
from courtiq.domains.competitions.repository import CompetitionsRepository

logger = get_logger("ingestion.runner")


@dataclass
class IngestionResult:
    """Summary record of a domain ingestion execution."""
    domain: str
    status: str
    categories_ingested: int = 0
    competitions_ingested: int = 0
    records_ingested: int = 0
    errors: int = 0
    message: str = ""


class IngestionRunner:
    """Central orchestrator for CourtIQ data extraction, transformation, and loading."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None) -> None:
        """Initialize IngestionRunner.

        Args:
            db_manager: DatabaseManager instance. If None, uses default get_db().
        """
        self.db = db_manager or get_db()

    def run_migrations_if_needed(self) -> List[str]:
        """Apply any outstanding DDL migrations before ingestion."""
        logger.info("Checking and applying pending database migrations...")
        applied = self.db.run_migrations()
        return applied

    def ingest_competitions(
        self,
        extractor: Optional[CompetitionsExtractor] = None,
        transformer: Optional[CompetitionsTransformer] = None,
        repository: Optional[CompetitionsRepository] = None,
    ) -> IngestionResult:
        """Execute full end-to-end ingestion for the Competitions & Categories domain.

        Args:
            extractor: Optional custom CompetitionsExtractor.
            transformer: Optional custom CompetitionsTransformer.
            repository: Optional custom CompetitionsRepository.

        Returns:
            IngestionResult object with execution statistics.
        """
        logger.info(">>> Starting Competitions Domain Ingestion Pipeline <<<")
        self.run_migrations_if_needed()

        ext = extractor or CompetitionsExtractor()
        trans = transformer or CompetitionsTransformer()
        repo = repository or CompetitionsRepository(self.db)

        try:
            # 1. Extraction
            raw_payload = ext.extract()

            # 2. Transformation
            categories, competitions = trans.transform(raw_payload)

            # 3. Persistence
            saved_cats = repo.save_categories(categories)
            saved_comps = repo.save_competitions(competitions)

            logger.info(
                "Ingestion SUCCESS: %d categories and %d competitions saved.",
                saved_cats,
                saved_comps,
            )
            return IngestionResult(
                domain="competitions",
                status="SUCCESS",
                categories_ingested=saved_cats,
                competitions_ingested=saved_comps,
                records_ingested=saved_cats + saved_comps,
                message=f"Successfully persisted {saved_cats} categories and {saved_comps} competitions.",
            )

        except Exception as e:
            logger.error("Competitions ingestion pipeline failed: %s", e, exc_info=True)
            return IngestionResult(
                domain="competitions",
                status="FAILED",
                errors=1,
                message=str(e),
            )
