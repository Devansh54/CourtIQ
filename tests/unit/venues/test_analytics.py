
import pandas as pd
import pytest
import plotly.graph_objects as go

from unittest.mock import MagicMock

from courtiq.domains.venues.analytics import VenuesAnalytics


@pytest.fixture
def mock_repository():
    repo = MagicMock()

    repo.get_complex_count.return_value = 5
    repo.get_venue_count.return_value = 11

    repo.query_1_venues_with_complex.return_value = pd.DataFrame({
        "city_name": ["Melbourne", "Santiago", "Paris"],
        "complex_name": ["Melbourne Park", "Estadio Nacional", "Roland Garros"],
    })

    repo.query_6_venues_by_country_group.return_value = pd.DataFrame({
        "country_name": ["Australia", "Chile", "France"],
        "country_code": ["AUS", "CHL", "FRA"],
        "total_venues": [3, 2, 2],
    })

    repo.query_2_venues_count_per_complex.return_value = pd.DataFrame({
        "complex_name": ["Melbourne Park", "Estadio Nacional"],
        "total_venues": [3, 2],
    })

    repo.query_4_venues_and_timezones.return_value = pd.DataFrame({
        "timezone": [
            "Australia/Melbourne",
            "Australia/Melbourne",
            "America/Santiago",
        ]
    })

    return repo


@pytest.fixture
def analytics(mock_repository):
    return VenuesAnalytics(repository=mock_repository)


def test_summary_kpis(analytics):
    kpis = analytics.get_summary_kpis()

    assert kpis["total_complexes"] == 5
    assert kpis["total_venues"] == 11
    assert kpis["total_countries"] == 3
    assert kpis["total_cities"] == 3
    assert kpis["average_venues_per_complex"] == 2.2


def test_summary_kpis_when_database_empty(mock_repository):
    mock_repository.get_complex_count.return_value = 0
    mock_repository.get_venue_count.return_value = 0
    mock_repository.query_1_venues_with_complex.return_value = pd.DataFrame()
    mock_repository.query_6_venues_by_country_group.return_value = pd.DataFrame()

    kpis = VenuesAnalytics(mock_repository).get_summary_kpis()

    assert kpis["total_complexes"] == 0
    assert kpis["total_venues"] == 0
    assert kpis["total_countries"] == 0
    assert kpis["total_cities"] == 0
    assert kpis["average_venues_per_complex"] == 0


def test_country_bar_chart(analytics):
    chart = analytics.create_country_bar_chart()

    assert isinstance(chart, go.Figure)
    assert len(chart.data) == 1
    assert chart.layout.title.text == "Venues by Country"


def test_country_chart_empty_data(mock_repository):
    mock_repository.query_6_venues_by_country_group.return_value = pd.DataFrame()

    chart = VenuesAnalytics(mock_repository).create_country_bar_chart()

    assert isinstance(chart, go.Figure)
    assert len(chart.data) == 0


def test_complex_bar_chart(analytics):
    chart = analytics.create_complex_bar_chart()

    assert isinstance(chart, go.Figure)
    assert len(chart.data) == 1
    assert chart.layout.title.text == "Venues per Complex"


def test_complex_chart_empty_data(mock_repository):
    mock_repository.query_2_venues_count_per_complex.return_value = pd.DataFrame()

    chart = VenuesAnalytics(mock_repository).create_complex_bar_chart()

    assert isinstance(chart, go.Figure)
    assert len(chart.data) == 0


def test_timezone_pie_chart(analytics):
    chart = analytics.create_timezone_pie_chart()

    assert isinstance(chart, go.Figure)
    assert len(chart.data) == 1
    assert chart.layout.title.text == "Venues by Timezone"


def test_timezone_chart_empty_data(mock_repository):
    mock_repository.query_4_venues_and_timezones.return_value = pd.DataFrame()

    chart = VenuesAnalytics(mock_repository).create_timezone_pie_chart()

    assert isinstance(chart, go.Figure)
    assert len(chart.data) == 0
