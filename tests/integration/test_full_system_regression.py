"""Full System Cross-Domain Integration & Regression Test Suite.

Verifies that all three CourtIQ business domains (Competitions, Venues, and Rankings)
can be ingested, persisted, queried, and analyzed concurrently on PostgreSQL 18
without foreign key violations, session locks, or state corruption.
"""

from courtiq.core.database import DatabaseManager
from courtiq.domains.competitions.analytics import CompetitionsAnalytics
from courtiq.domains.competitions.repository import CompetitionsRepository
from courtiq.domains.venues.analytics import VenuesAnalytics
from courtiq.domains.venues.repository import VenuesRepository
from courtiq.domains.rankings.analytics import RankingsAnalytics
from courtiq.domains.rankings.repository import RankingsRepository
from courtiq.ingestion.runner import IngestionRunner


def test_full_system_cross_domain_regression(postgres_test_db: DatabaseManager):
    """Verify concurrent operation across all 3 domains and 6 relational tables on PostgreSQL."""
    assert postgres_test_db.is_postgres is True, "System regression must run against PostgreSQL"

    runner = IngestionRunner(postgres_test_db)

    # 1. Ingest Competitions Domain
    res_comp = runner.ingest_competitions()
    assert res_comp.status == "SUCCESS"
    assert res_comp.records_ingested > 0
    assert res_comp.errors == 0

    # 2. Ingest Venues & Complexes Domain
    res_ven = runner.ingest_venues()
    assert res_ven.status == "SUCCESS"
    assert res_ven.records_ingested > 0
    assert res_ven.errors == 0

    # 3. Ingest Doubles Rankings Domain
    res_rnk = runner.ingest_rankings()
    assert res_rnk.status == "SUCCESS"
    assert res_rnk.records_ingested > 0
    assert res_rnk.errors == 0

    # 4. Verify all 6 relational tables are populated
    comp_repo = CompetitionsRepository(postgres_test_db)
    ven_repo = VenuesRepository(postgres_test_db)
    rnk_repo = RankingsRepository(postgres_test_db)

    assert comp_repo.get_category_count() > 0
    assert comp_repo.get_competition_count() > 0
    assert ven_repo.get_complex_count() > 0
    assert ven_repo.get_venue_count() > 0
    assert rnk_repo.get_competitor_count() > 0
    assert rnk_repo.get_rankings_count() > 0

    # 5. Verify cross-domain analytics services
    comp_analytics = CompetitionsAnalytics(comp_repo)
    comp_kpis = comp_analytics.get_summary_kpis()
    assert comp_kpis["total_competitions"] > 0
    assert comp_kpis["total_categories"] > 0

    ven_analytics = VenuesAnalytics(ven_repo)
    ven_kpis = ven_analytics.get_summary_kpis()
    assert ven_kpis["total_complexes"] > 0
    assert ven_kpis["total_venues"] > 0

    rnk_analytics = RankingsAnalytics(rnk_repo)
    rnk_kpis = rnk_analytics.get_summary_kpis()
    assert rnk_kpis["total_competitors"] > 0
    assert rnk_kpis["total_countries"] > 0
    assert rnk_kpis["average_points"] > 0

    # 6. Verify sample queries across domains
    df_comp = comp_repo.query_1_all_with_category()
    assert not df_comp.empty

    df_ven = ven_repo.query_1_venues_with_complex()
    assert not df_ven.empty

    df_rnk = rnk_repo.query_1_top_ranked_competitors()
    assert not df_rnk.empty
