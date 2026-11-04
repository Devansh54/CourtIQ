"""Integration tests for CourtIQ Competitions End-to-End Pipeline."""

from pathlib import Path
from courtiq.core.database import DatabaseManager
from courtiq.domains.competitions.analytics import CompetitionsAnalytics
from courtiq.domains.competitions.repository import CompetitionsRepository
from courtiq.ingestion.runner import IngestionRunner


def test_competitions_end_to_end_pipeline(tmp_path: Path):
    """Test full execution: Migrations -> Extraction -> Transformation -> SQL Storage -> Analytics."""
    db_file = tmp_path / "integration_courtiq.db"
    db_mgr = DatabaseManager(db_file)

    runner = IngestionRunner(db_mgr)
    result = runner.ingest_competitions()

    assert result.status == "SUCCESS"
    assert result.categories_ingested > 0
    assert result.competitions_ingested > 0
    assert result.errors == 0

    # Verify repository access
    repo = CompetitionsRepository(db_mgr)
    assert repo.get_competition_count() == result.competitions_ingested
    assert repo.get_category_count() == result.categories_ingested

    # Verify analytics calculations
    analytics = CompetitionsAnalytics(repo)
    kpis = analytics.get_summary_kpis()

    assert kpis["total_competitions"] > 0
    assert kpis["total_categories"] > 0
    assert kpis["doubles_count"] > 0
    assert kpis["singles_count"] > 0

    # Verify chart generation without crash
    fig_bar = analytics.create_category_bar_chart()
    assert fig_bar is not None

    fig_pie = analytics.create_type_sunburst_or_pie()
    assert fig_pie is not None

    fig_stacked = analytics.create_type_distribution_stacked_bar()
    assert fig_stacked is not None
