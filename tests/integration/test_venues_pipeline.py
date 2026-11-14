"""Integration tests for CourtIQ Venues End-to-End Pipeline."""

from courtiq.core.database import DatabaseManager
from courtiq.domains.venues.analytics import VenuesAnalytics
from courtiq.domains.venues.repository import VenuesRepository
from courtiq.ingestion.runner import IngestionRunner


def test_venues_end_to_end_pipeline(postgres_test_db: DatabaseManager):
    """Test full execution: Migrations -> Extraction -> Transformation -> SQL Storage -> Analytics on PostgreSQL."""
    assert postgres_test_db.is_postgres is True, "Pipeline integration test must run against PostgreSQL"
    runner = IngestionRunner(postgres_test_db)
    result = runner.ingest_venues()

    assert result.status == "SUCCESS"
    assert result.records_ingested > 0
    assert result.errors == 0

    # Verify repository access
    repo = VenuesRepository(postgres_test_db)
    assert repo.get_complex_count() > 0
    assert repo.get_venue_count() > 0

    # Verify all 7 analytical queries execute on PostgreSQL
    df_q1 = repo.query_1_venues_with_complex()
    assert not df_q1.empty
    assert "venue_name" in df_q1.columns
    assert "complex_name" in df_q1.columns

    df_q2 = repo.query_2_venues_count_per_complex()
    assert not df_q2.empty
    assert "total_venues" in df_q2.columns

    df_q3 = repo.query_3_venues_by_country(country="Australia")
    assert not df_q3.empty
    assert all(c.lower() == "australia" for c in df_q3["country_name"])

    df_q4 = repo.query_4_venues_and_timezones()
    assert not df_q4.empty
    assert "timezone" in df_q4.columns

    df_q5 = repo.query_5_multi_venue_complexes()
    assert not df_q5.empty
    assert all(v > 1 for v in df_q5["total_venues"])

    df_q6 = repo.query_6_venues_by_country_group()
    assert not df_q6.empty
    assert "total_venues" in df_q6.columns

    df_q7 = repo.query_7_venues_for_specific_complex(complex_name="Melbourne")
    assert not df_q7.empty
    assert "Melbourne" in df_q7.iloc[0]["complex_name"]

    # Verify analytics calculations
    analytics = VenuesAnalytics(repo)
    kpis = analytics.get_summary_kpis()

    assert kpis["total_complexes"] > 0
    assert kpis["total_venues"] > 0
    assert kpis["total_countries"] > 0
    assert kpis["total_cities"] > 0
    assert kpis["average_venues_per_complex"] > 0

    # Verify chart generation without crash
    fig_country = analytics.create_country_bar_chart()
    assert fig_country is not None

    fig_complex = analytics.create_complex_bar_chart()
    assert fig_complex is not None

    fig_tz = analytics.create_timezone_pie_chart()
    assert fig_tz is not None
