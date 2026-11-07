"""CourtIQ Sportradar API Client.

Handles HTTP communication with the Sportradar Tennis API (v3) with
strict rate limiting, exponential backoff retries, custom exception mapping,
and synthetic demonstration fixture loading in DEMO mode.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional
import requests

from courtiq.core.config import Settings, get_settings
from courtiq.core.exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
)
from courtiq.core.logging_config import get_logger

logger = get_logger("core.api_client")


class SportradarClient:
    """Robust client for Sportradar Tennis API v3."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Initialize SportradarClient.

        Args:
            settings: Settings instance. If None, uses get_settings().
        """
        self.settings = settings or get_settings()
        self.base_url = self.settings.sportradar_base_url
        self.api_key = self.settings.sportradar_api_key
        self.timeout = self.settings.sportradar_timeout
        self.rate_limit_interval = 1.0 / max(0.1, self.settings.sportradar_rate_limit_rps)
        self.max_retries = self.settings.sportradar_max_retries
        self.backoff_factor = self.settings.sportradar_backoff_factor

        self._last_request_time: float = 0.0
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create and configure requests Session with standard headers."""
        session = requests.Session()
        session.headers.update({
            "Accept": "application/json",
            "User-Agent": "CourtIQ-Analytics/0.1.0",
        })
        return session

    def _enforce_rate_limit(self) -> None:
        """Ensure minimum interval between consecutive outgoing requests to adhere to 1 RPS."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.rate_limit_interval:
            sleep_duration = self.rate_limit_interval - elapsed
            logger.debug("Rate limiter: sleeping for %.3f seconds", sleep_duration)
            time.sleep(sleep_duration)
        self._last_request_time = time.time()

    def _load_fixture_fallback(self, endpoint: str) -> Dict[str, Any]:
        """Load synthetic fixture for DEMO mode. Clearly logs and identifies synthetic data."""
        fixture_map = {
            "competitions": "competitions_sample.json",
            "complexes": "complexes_sample.json",
            "rankings": "rankings_sample.json",
            "doubles": "rankings_sample.json",
        }

        matched_file = None
        for key, fname in fixture_map.items():
            if key in endpoint.lower():
                matched_file = fname
                break

        if not matched_file:
            matched_file = "competitions_sample.json"

        fixture_path = self.settings.fixtures_dir / matched_file
        if not fixture_path.exists():
            raise ResourceNotFoundError(
                f"Synthetic fixture not found at {fixture_path} for endpoint {endpoint}"
            )

        logger.info(
            "[DEMO MODE] Loading synthetic demonstration fixture from '%s' for endpoint '%s'",
            fixture_path.name,
            endpoint,
        )
        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            # Annotate top-level metadata identifying data as synthetic demonstration
            data.setdefault("_synthetic", True)
            data.setdefault("_source", f"fixture:{fixture_path.name}")

        return data

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute GET request against Sportradar API with retries and rate limiting.

        In DEMO mode:
            Loads synthetic test fixtures without making external network calls.

        In LIVE mode:
            Requires a valid SPORTRADAR_API_KEY. Makes real network requests against
            the Sportradar API. NEVER falls back to synthetic fixtures on failure.
            Raises AuthenticationError, RateLimitError, or APIError.

        Args:
            endpoint: API endpoint path (e.g., 'competitions.json' or '/competitions.json').
            params: Optional query parameters.

        Returns:
            Parsed JSON dictionary from API response or synthetic fixture.

        Raises:
            AuthenticationError: Missing/placeholder API key or HTTP 401/403.
            RateLimitError: HTTP 429 when max retries are exhausted.
            ResourceNotFoundError: HTTP 404 resource not found or fixture missing.
            APIError: HTTP 5xx, unexpected response, or network failure after max retries.
        """
        # DEMO Mode: explicitly load synthetic fixture without network calls
        if self.settings.is_demo_mode:
            logger.info("DEMO mode active. Serving synthetic demonstration fixture.")
            return self._load_fixture_fallback(endpoint)

        # LIVE Mode: Validate API key before attempting request
        if not self.settings.has_valid_api_key:
            logger.error("LIVE mode active but SPORTRADAR_API_KEY is missing or set to placeholder.")
            raise AuthenticationError(
                "Sportradar API key is missing or set to a placeholder in LIVE mode. "
                "Configure a valid SPORTRADAR_API_KEY in .env or switch to COURTIQ_MODE=DEMO."
            )

        clean_endpoint = endpoint.lstrip("/")
        if not clean_endpoint.endswith(f".{self.settings.sportradar_format}"):
            clean_endpoint = f"{clean_endpoint}.{self.settings.sportradar_format}"

        url = f"{self.base_url}/{clean_endpoint}"
        query_params = dict(params or {})
        query_params["api_key"] = self.api_key

        attempt = 0
        backoff = self.backoff_factor

        while attempt < self.max_retries:
            attempt += 1
            self._enforce_rate_limit()

            try:
                logger.debug("Dispatching API GET to %s (attempt %d/%d)", url, attempt, self.max_retries)
                response = self.session.get(url, params=query_params, timeout=self.timeout)

                if response.status_code == 200:
                    return response.json()

                if response.status_code in (401, 403):
                    logger.error("Sportradar API authentication rejected with status %d", response.status_code)
                    raise AuthenticationError(
                        f"Sportradar API authentication failed ({response.status_code}): Check SPORTRADAR_API_KEY in .env"
                    )

                if response.status_code == 404:
                    logger.error("Endpoint %s not found (404)", url)
                    raise ResourceNotFoundError(clean_endpoint)

                if response.status_code == 429:
                    logger.warning("Rate limit hit (429) on attempt %d. Backing off for %.2fs", attempt, backoff)
                    if attempt >= self.max_retries:
                        raise RateLimitError("Rate limit exceeded and max retries exhausted.")
                    time.sleep(backoff)
                    backoff *= 2
                    continue

                if response.status_code >= 500:
                    logger.warning("Server error %d on attempt %d. Backing off for %.2fs", response.status_code, attempt, backoff)
                    if attempt >= self.max_retries:
                        raise APIError(
                            f"Sportradar server error {response.status_code} after {self.max_retries} attempts.",
                            status_code=response.status_code,
                        )
                    time.sleep(backoff)
                    backoff *= 2
                    continue

                # Any other unexpected status
                raise APIError(
                    f"Unexpected API response {response.status_code}: {response.text}",
                    status_code=response.status_code,
                )

            except requests.RequestException as e:
                logger.warning("Network/HTTP error on attempt %d/%d: %s", attempt, self.max_retries, e)
                if attempt >= self.max_retries:
                    raise APIError(
                        f"Sportradar API request failed after {self.max_retries} retries: {e}"
                    )
                time.sleep(backoff)
                backoff *= 2

        raise APIError(f"Sportradar API request to '{clean_endpoint}' failed after {self.max_retries} attempts.")
