"""Unit tests for Sportradar API client."""

import time
from courtiq.core.api_client import SportradarClient
from courtiq.core.config import Settings


def test_api_client_mock_fallback(fixtures_dir):
    """Verify that client returns mock fixture data when in mock mode."""
    settings = Settings()
    client = SportradarClient(settings)

    payload = client.get("competitions.json")
    assert isinstance(payload, dict)
    assert "competitions" in payload
    assert len(payload["competitions"]) > 0


def test_api_client_rate_limiting():
    """Verify that rate limiter enforces minimum delay between consecutive calls."""
    settings = Settings()
    # Configure high interval for testability (e.g. 5 RPS -> 0.2s interval)
    settings.sportradar_rate_limit_rps = 5.0
    client = SportradarClient(settings)

    start = time.time()
    client._enforce_rate_limit()
    client._enforce_rate_limit()
    elapsed = time.time() - start

    assert elapsed >= 0.18
