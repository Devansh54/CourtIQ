"""CourtIQ Configuration Management.

Loads configuration from environment variables and .env files with
strict validation, PostgreSQL connection settings, and dual-mode execution.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Ensure .env is loaded from project root if present
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


class Settings:
    """Application configuration container."""

    def __init__(self) -> None:
        self.project_root: Path = _PROJECT_ROOT
        self.env: str = os.getenv("COURTIQ_ENV", "development").lower()

        # Operating Mode (LIVE: real API calls with strict auth | DEMO: synthetic fixtures)
        raw_mode = os.getenv("COURTIQ_MODE")
        if raw_mode:
            self.courtiq_mode: str = raw_mode.upper()
        else:
            key = os.getenv("SPORTRADAR_API_KEY")
            is_placeholder = not key or key.strip().lower() in [
                "your_sportradar_api_key_here", "placeholder", "changeme", "none", "test_key"
            ]
            self.courtiq_mode: str = "DEMO" if is_placeholder else "LIVE"

        # Sportradar API Settings
        self.sportradar_api_key: Optional[str] = os.getenv("SPORTRADAR_API_KEY")
        self.sportradar_base_url: str = os.getenv(
            "SPORTRADAR_BASE_URL", "https://api.sportradar.com/tennis/trial/v3/en"
        ).rstrip("/")
        self.sportradar_format: str = os.getenv("SPORTRADAR_FORMAT", "json").lower()
        self.sportradar_timeout: int = int(os.getenv("SPORTRADAR_TIMEOUT", "15"))
        self.sportradar_rate_limit_rps: float = float(os.getenv("SPORTRADAR_RATE_LIMIT_RPS", "1.0"))
        self.sportradar_max_retries: int = int(os.getenv("SPORTRADAR_MAX_RETRIES", "3"))
        self.sportradar_backoff_factor: float = float(os.getenv("SPORTRADAR_BACKOFF_FACTOR", "1.5"))

        # Primary Database Configuration (PostgreSQL 16+ via Psycopg 3)
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://courtiq_app:courtiq_app_password@127.0.0.1:5432/courtiq",
        )

        # Migration Database Configuration (Dedicated DDL role)
        self.migration_database_url: str = os.getenv(
            "MIGRATION_DATABASE_URL",
            os.getenv(
                "DATABASE_URL",
                "postgresql+psycopg://courtiq_migrator:courtiq_migrator_password@127.0.0.1:5432/courtiq",
            ),
        )

        # Optional Integration Test Database URL
        self.test_database_url: Optional[str] = os.getenv("TEST_DATABASE_URL")

        # Database Connection Pool Settings
        self.db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
        self.db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        self.db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.db_pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))
        self.db_pool_pre_ping: bool = os.getenv("DB_POOL_PRE_PING", "true").lower() in ("true", "1", "yes")

        # Legacy SQLite Path (retained for migration utility and test fallback)
        default_db_rel = os.getenv("COURTIQ_DB_PATH", "data/courtiq.db")
        self.courtiq_db_path: Path = (
            Path(default_db_rel)
            if Path(default_db_rel).is_absolute()
            else self.project_root / default_db_rel
        )

        # Logging
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def is_demo_mode(self) -> bool:
        """Return True if running in DEMO mode."""
        if self.courtiq_mode == "DEMO":
            return True
        if self.courtiq_mode == "LIVE":
            return False
        placeholder_indicators = [
            "your_sportradar_api_key_here",
            "placeholder",
            "changeme",
            "none",
            "test_key",
        ]
        return not self.sportradar_api_key or self.sportradar_api_key.strip().lower() in placeholder_indicators

    @property
    def is_mock_mode(self) -> bool:
        """Alias for is_demo_mode for backward compatibility."""
        return self.is_demo_mode

    @property
    def is_postgres(self) -> bool:
        """Return True if configured database engine is PostgreSQL."""
        return self.database_url.lower().startswith("postgresql")

    @property
    def db_dialect(self) -> str:
        """Return detected database dialect ('postgresql', 'sqlite', etc.)."""
        if self.database_url.lower().startswith("postgresql"):
            return "postgresql"
        if self.database_url.lower().startswith("sqlite"):
            return "sqlite"
        return self.database_url.split(":", 1)[0].split("+", 1)[0]

    @property
    def fixtures_dir(self) -> Path:
        """Directory path containing test and offline fixtures."""
        return self.project_root / "tests" / "fixtures"

    @property
    def migrations_dir(self) -> Path:
        """Directory path containing legacy SQL migrations."""
        return self.project_root / "sql" / "migrations"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached singleton application settings."""
    return Settings()
