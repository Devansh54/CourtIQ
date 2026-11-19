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
from courtiq.domains.venues.extractor import VenuesExtractor
from courtiq.domains.venues.transformer import VenuesTransformer
from courtiq.domains.venues.repository import VenuesRepository
from courtiq.domains.rankings.extractor import RankingsExtractor
from courtiq.domains.rankings.transformer import RankingsTransformer
from courtiq.domains.rankings.repository import RankingsRepository

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

    def ingest_venues(
        self,
        extractor: Optional[VenuesExtractor] = None,
        transformer: Optional[VenuesTransformer] = None,
        repository: Optional[VenuesRepository] = None,
    ) -> IngestionResult:
        """Execute the Venues ingestion pipeline."""

        logger.info("Starting Venues ingestion pipeline")

        try:
            self.run_migrations_if_needed()

            ext = extractor or VenuesExtractor()
            trans = transformer or VenuesTransformer()
            repo = repository or VenuesRepository(self.db)

            raw_payload = ext.extract()

            complexes, venues = trans.transform(raw_payload)

            saved_complexes = repo.save_complexes(complexes)
            saved_venues = repo.save_venues(venues)

            total = saved_complexes + saved_venues

            logger.info(
                "Venues ingestion successful: %d complexes, %d venues",
                saved_complexes,
                saved_venues,
            )

            return IngestionResult(
                domain="venues",
                status="SUCCESS",
                records_ingested=total,
                message=(
                    f"Successfully saved {saved_complexes} complexes "
                    f"and {saved_venues} venues."
                ),
            )

        except Exception as e:
            logger.error(
                "Venues ingestion failed: %s",
                e,
                exc_info=True,
            )

            return IngestionResult(
                domain="venues",
                status="FAILED",
                errors=1,
                message=str(e),
            )

    def ingest_rankings(
        self,
        extractor: Optional[RankingsExtractor] = None,
        transformer: Optional[RankingsTransformer] = None,
        repository: Optional[RankingsRepository] = None,
    ) -> IngestionResult:
        """Execute the Doubles Competitor Rankings ingestion pipeline."""

        try:
            self.run_migrations_if_needed()

            ext = extractor or RankingsExtractor()
            trans = transformer or RankingsTransformer()
            repo = repository or RankingsRepository(self.db)

            raw_payload = ext.extract()
            competitors, rankings = trans.transform(raw_payload)

            saved_competitors = repo.save_competitors(competitors)
            saved_rankings = repo.save_rankings(rankings)

            total_records = saved_competitors + saved_rankings

            logger.info(
                "Rankings ingestion successful: %d competitors and %d rankings",
                saved_competitors,
                saved_rankings,
            )

            return IngestionResult(
                domain="rankings",
                status="SUCCESS",
                records_ingested=total_records,
                message=(
                    f"Successfully saved {saved_competitors} competitors "
                    f"and {saved_rankings} rankings."
                ),
            )

        except Exception as exc:
            logger.error(
                "Rankings ingestion failed: %s",
                exc,
                exc_info=True,
            )

            return IngestionResult(
                domain="rankings",
                status="FAILED",
                errors=1,
                message=str(exc),
            )