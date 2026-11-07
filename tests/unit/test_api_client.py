"""Unit tests for Sportradar API client.

Verifies DEMO vs. LIVE mode behavior, rate limiting, retry semantics,
strict non-fallback guarantees in LIVE mode, and prevention of API key leakage in logs/exceptions.
"""

import time
from unittest.mock import MagicMock, patch
import pytest
import requests

from courtiq.core.api_client import SportradarClient
from courtiq.core.config import Settings
from courtiq.core.exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
)


def _create_mock_response(status_code: int, json_data: dict = None, text: str = "") -> MagicMock:
    """Helper to create a mock requests.Response object."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.text = text or f"Response with status {status_code}"
    if json_data is not None:
        mock_resp.json.return_value = json_data
    else:
        mock_resp.json.side_effect = ValueError("No JSON")
    return mock_resp


# --- DEMO MODE TESTS ---


def test_demo_mode_fixture_loading(fixtures_dir):
    """Verify that in DEMO mode, client returns synthetic fixtures without network calls."""
    settings = Settings()
    settings.courtiq_mode = "DEMO"
    client = SportradarClient(settings)

    with patch.object(client.session, "get") as mock_get:
        payload = client.get("competitions.json")

        assert isinstance(payload, dict)
        assert "competitions" in payload
        assert len(payload["competitions"]) > 0
        assert payload.get("_synthetic") is True
        assert "fixture:" in payload.get("_source", "")
        # Session.get must NOT be called in DEMO mode
        mock_get.assert_not_called()


# --- LIVE MODE TESTS ---


def test_live_mode_successful_response():
    """Verify that in LIVE mode with a valid key, client executes HTTP request."""
    settings = Settings()
    settings.courtiq_mode = "LIVE"
    settings.sportradar_api_key = "live_valid_test_key_12345"
    settings.sportradar_rate_limit_rps = 100.0  # Fast rate limit for test
    client = SportradarClient(settings)

    expected_data = {"competitions": [{"id": "sr:competition:1", "name": "French Open"}]}
    mock_response = _create_mock_response(200, json_data=expected_data)

    with patch.object(client.session, "get", return_value=mock_response) as mock_get:
        payload = client.get("competitions.json")

        assert payload == expected_data
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args.kwargs
        assert call_kwargs["params"]["api_key"] == "live_valid_test_key_12345"


def test_live_mode_missing_api_key():
    """Verify that LIVE mode fails immediately when API key is missing, empty, or whitespace-only."""
    for blank_key in ["", "   ", "\t  \n  ", None]:
        settings = Settings()
        settings.courtiq_mode = "LIVE"
        settings.sportradar_api_key = blank_key
        client = SportradarClient(settings)

        with patch.object(client.session, "get") as mock_get:
            with pytest.raises(AuthenticationError, match="Sportradar API key is missing or set to a placeholder"):
                client.get("competitions.json")
            mock_get.assert_not_called()


def test_live_mode_placeholder_api_key():
    """Verify that LIVE mode rejects placeholder API keys without network calls."""
    settings = Settings()
    settings.courtiq_mode = "LIVE"
    settings.sportradar_api_key = "your_sportradar_api_key_here"
    client = SportradarClient(settings)

    with patch.object(client.session, "get") as mock_get:
        with pytest.raises(AuthenticationError, match="placeholder in LIVE mode"):
            client.get("competitions.json")
        mock_get.assert_not_called()


def test_live_mode_auth_rejection_401():
    """Verify that LIVE mode raises AuthenticationError on 401 Unauthorized without fallback."""
    settings = Settings()
    settings.courtiq_mode = "LIVE"
    settings.sportradar_api_key = "live_valid_test_key_12345"
    settings.sportradar_rate_limit_rps = 100.0
    client = SportradarClient(settings)

    mock_resp = _create_mock_response(401, text="Unauthorized API key")
    with patch.object(client.session, "get", return_value=mock_resp):
        with patch.object(client, "_load_fixture_fallback") as mock_fallback:
            with pytest.raises(AuthenticationError, match="authentication failed \\(401\\)"):
                client.get("competitions.json")
            mock_fallback.assert_not_called()


def test_live_mode_rate_limit_429():
    """Verify that LIVE mode retries on 429 and raises RateLimitError when retries exhaust."""
    settings = Settings()
    settings.courtiq_mode = "LIVE"
    settings.sportradar_api_key = "live_valid_test_key_12345"
    settings.sportradar_max_retries = 2
    settings.sportradar_backoff_factor = 0.01
    settings.sportradar_rate_limit_rps = 100.0
    client = SportradarClient(settings)

    mock_resp = _create_mock_response(429, text="Rate limit exceeded")
    with patch.object(client.session, "get", return_value=mock_resp) as mock_get:
        with patch.object(client, "_load_fixture_fallback") as mock_fallback:
            with pytest.raises(RateLimitError, match="Rate limit exceeded"):
                client.get("competitions.json")
            assert mock_get.call_count == 2
            mock_fallback.assert_not_called()


def test_live_mode_network_timeout_after_retries():
    """Verify that LIVE mode raises APIError on network timeouts and never falls back."""
    settings = Settings()
    settings.courtiq_mode = "LIVE"
    settings.sportradar_api_key = "live_valid_test_key_12345"
    settings.sportradar_max_retries = 2
    settings.sportradar_backoff_factor = 0.01
    settings.sportradar_rate_limit_rps = 100.0
    client = SportradarClient(settings)

    with patch.object(client.session, "get", side_effect=requests.Timeout("Connection timed out")) as mock_get:
        with patch.object(client, "_load_fixture_fallback") as mock_fallback:
            with pytest.raises(APIError, match="Sportradar API request to 'competitions.json' failed after 2 retries"):
                client.get("competitions.json")
            assert mock_get.call_count == 2
            # Crucial assertion: Must NEVER fall back to fixtures
            mock_fallback.assert_not_called()


def test_live_mode_never_falls_back_on_server_error():
    """Verify that LIVE mode raises APIError on 500 server error and never loads fixtures."""
    settings = Settings()
    settings.courtiq_mode = "LIVE"
    settings.sportradar_api_key = "live_valid_test_key_12345"
    settings.sportradar_max_retries = 2
    settings.sportradar_backoff_factor = 0.01
    settings.sportradar_rate_limit_rps = 100.0
    client = SportradarClient(settings)

    mock_resp = _create_mock_response(500, text="Internal Server Error")
    with patch.object(client.session, "get", return_value=mock_resp) as mock_get:
        with patch.object(client, "_load_fixture_fallback") as mock_fallback:
            with pytest.raises(APIError, match="Sportradar server error 500"):
                client.get("competitions.json")
            assert mock_get.call_count == 2
            mock_fallback.assert_not_called()


def test_api_client_rate_limiting():
    """Verify that rate limiter enforces minimum delay between consecutive calls."""
    settings = Settings()
    settings.sportradar_rate_limit_rps = 5.0  # 0.2s interval
    client = SportradarClient(settings)

    start = time.time()
    client._enforce_rate_limit()
    client._enforce_rate_limit()
    elapsed = time.time() - start

    assert elapsed >= 0.18


# --- SECURITY & SENSITIVE CREDENTIAL LEAKAGE TESTS ---


def test_live_mode_does_not_leak_api_key_on_connection_error(caplog):
    """Verify that sensitive API keys are not leaked in logs or APIError messages on connection failure."""
    fake_secret = "secret_api_key_xyz_98765"
    settings = Settings()
    settings.courtiq_mode = "LIVE"
    settings.sportradar_api_key = fake_secret
    settings.sportradar_max_retries = 2
    settings.sportradar_backoff_factor = 0.01
    settings.sportradar_rate_limit_rps = 100.0
    client = SportradarClient(settings)

    leaked_url = f"https://api.sportradar.com/tennis/trial/v3/en/competitions.json?api_key={fake_secret}"
    sensitive_err_msg = f"HTTPSConnectionPool(host='api.sportradar.com', port=443): Failed to establish connection with url: {leaked_url}"

    with caplog.at_level("DEBUG"):
        with patch.object(client.session, "get", side_effect=requests.ConnectionError(sensitive_err_msg)):
            with pytest.raises(APIError) as exc_info:
                client.get("competitions.json")

    # 1. Verify fake secret does NOT appear anywhere in captured log text
    assert fake_secret not in caplog.text
    # 2. Verify fake secret does NOT appear in the raised APIError message
    assert fake_secret not in str(exc_info.value)
    # 3. Verify chained exception suppression (from None) prevents leakage via __cause__
    assert exc_info.value.__cause__ is None


def test_live_mode_does_not_leak_api_key_on_unexpected_response(caplog):
    """Verify that unexpected HTTP response bodies echoing sensitive parameters do not leak into APIError or logs."""
    fake_secret = "secret_api_key_xyz_98765"
    settings = Settings()
    settings.courtiq_mode = "LIVE"
    settings.sportradar_api_key = fake_secret
    settings.sportradar_rate_limit_rps = 100.0
    client = SportradarClient(settings)

    sensitive_response_body = f'{{"error": "Invalid request for key {fake_secret}"}}'
    mock_resp = _create_mock_response(418, text=sensitive_response_body)

    with caplog.at_level("DEBUG"):
        with patch.object(client.session, "get", return_value=mock_resp):
            with pytest.raises(APIError) as exc_info:
                client.get("competitions.json")

    # 1. Verify fake secret does NOT appear in captured log text
    assert fake_secret not in caplog.text
    # 2. Verify fake secret does NOT appear in raised APIError message
    assert fake_secret not in str(exc_info.value)
    # 3. Verify HTTP status code is safely preserved
    assert exc_info.value.status_code == 418
