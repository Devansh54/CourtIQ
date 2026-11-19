"""Integration tests for CourtIQ Rankings End-to-End Pipeline."""

from courtiq.core.database import DatabaseManager
from courtiq.domains.rankings.analytics import RankingsAnalytics
from courtiq.domains.rankings.repository import RankingsRepository
from courtiq.ingestion.runner import IngestionRunner


def test_rankings_end_to_end_pipeline(
    postgres_test_db: DatabaseManager,
):
    """Test extraction, transformation, PostgreSQL storage and analytics."""

    assert postgres_test_db.is_postgres is True

    # Run complete Rankings ingestion pipeline.
    runner = IngestionRunner(postgres_test_db)
    result = runner.ingest_rankings()

    assert result.status == "SUCCESS"
    assert result.records_ingested > 0
    assert result.errors == 0

    # Verify repository records.
    repo = RankingsRepository(postgres_test_db)

    assert repo.get_competitor_count() > 0
    assert repo.get_rankings_count() > 0

    # Verify all six analytical SQL queries.
    df_q1 = repo.query_1_competitors_rank_points()
    assert not df_q1.empty

    df_q2 = repo.query_2_top_5_competitors()
    assert not df_q2.empty
    assert len(df_q2) <= 5

    df_q3 = repo.query_3_stable_rank_competitors()
    assert df_q3 is not None

    df_q4 = repo.query_4_points_by_country("Croatia")
    assert df_q4 is not None

    df_q5 = repo.query_5_competitors_per_country()
    assert not df_q5.empty

    df_q6 = repo.query_6_highest_points_competitors()
    assert not df_q6.empty

    # Verify analytics KPIs.
    analytics = RankingsAnalytics(repo)
    kpis = analytics.get_summary_kpis()

    assert kpis["total_competitors"] > 0
    assert kpis["total_countries"] > 0
    assert kpis["average_points"] > 0
    assert kpis["top_ranked_competitor"] != "N/A"
    assert kpis["biggest_rank_gainer"] != "N/A"