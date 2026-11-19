"""Unit tests for Rankings analytics."""

from courtiq.domains.rankings.analytics import RankingsAnalytics
from courtiq.domains.rankings.repository import RankingsRepository


def test_summary_kpis_with_empty_database(test_db):
    # Clear only Rankings data from the isolated test database.
    test_db.execute("DELETE FROM competitor_rankings")
    test_db.execute("DELETE FROM competitors")

    repository = RankingsRepository(db_manager=test_db)
    analytics = RankingsAnalytics(repository=repository)

    result = analytics.get_summary_kpis()

    assert result["total_competitors"] == 0
    assert result["total_countries"] == 0
    assert result["average_points"] == 0
    assert result["top_ranked_competitor"] == "N/A"
    assert result["biggest_rank_gainer"] == "N/A"