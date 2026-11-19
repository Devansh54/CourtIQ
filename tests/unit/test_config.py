"""Unit tests for configuration manager."""

import os
from courtiq.core.config import Settings, get_settings


def test_settings_defaults():
    """Verify settings loads default attributes safely."""
    settings = Settings()
    assert settings.sportradar_base_url.startswith("https://")
    assert settings.sportradar_timeout >= 5
    assert settings.sportradar_rate_limit_rps > 0
    assert settings.fixtures_dir.exists()
    assert settings.migrations_dir.exists()


def test_is_mock_mode_detection(monkeypatch):
    """Verify mock mode correctly triggers on empty, whitespace, or placeholder API keys."""
    monkeypatch.delenv("COURTIQ_MODE", raising=False)
    monkeypatch.setenv("SPORTRADAR_API_KEY", "your_sportradar_api_key_here")
    s1 = Settings()
    assert s1.is_mock_mode is True

    monkeypatch.setenv("SPORTRADAR_API_KEY", "   ")
    sw = Settings()
    assert sw.is_mock_mode is True
    assert sw.has_valid_api_key is False

    monkeypatch.setenv("SPORTRADAR_API_KEY", "real_api_key_12345")
    s2 = Settings()
    assert s2.is_mock_mode is False
    assert s2.has_valid_api_key is True


def test_get_settings_singleton():
    """Verify get_settings returns consistent cached settings."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
