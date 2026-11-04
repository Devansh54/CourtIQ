"""CourtIQ Configuration Management.

Loads configuration from environment variables and .env files with
type validation and safe defaults.
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

        # Database Settings
        # Default is zero-dependency SQLite relative to project root
        default_db_rel = os.getenv("COURTIQ_DB_PATH", "data/courtiq.db")
        self.courtiq_db_path: Path = (
            Path(default_db_rel)
            if Path(default_db_rel).is_absolute()
            else self.project_root / default_db_rel
        )
        self.database_url: str = os.getenv(
            "DATABASE_URL", f"sqlite:///{self.courtiq_db_path.as_posix()}"
        )

        # Logging
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def is_mock_mode(self) -> bool:
        """Determines if the application should use mock fixtures instead of live API."""
        if not self.sportradar_api_key:
            return True
        placeholder_indicators = [
            "your_sportradar_api_key_here",
            "placeholder",
            "changeme",
            "none",
            "test_key",
        ]
        return self.sportradar_api_key.strip().lower() in placeholder_indicators

    @property
    def fixtures_dir(self) -> Path:
        """Directory path containing test and offline fixtures."""
        return self.project_root / "tests" / "fixtures"

    @property
    def migrations_dir(self) -> Path:
        """Directory path containing SQL migrations."""
        return self.project_root / "sql" / "migrations"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached singleton application settings."""
    return Settings()
