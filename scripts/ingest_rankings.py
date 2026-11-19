"""Run the CourtIQ Rankings ingestion pipeline."""

import sys
from pathlib import Path

# Add the project source directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from courtiq.ingestion.runner import IngestionRunner


def main() -> None:
    """Execute Rankings ingestion."""

    print("Starting CourtIQ Rankings ingestion...")

    runner = IngestionRunner()
    result = runner.ingest_rankings()

    print("\n========== INGESTION RESULT ==========")
    print(f"Domain: {result.domain}")
    print(f"Status: {result.status}")
    print(f"Records ingested: {result.records_ingested}")
    print(f"Errors: {result.errors}")
    print(f"Message: {result.message}")
    print("======================================")


if __name__ == "__main__":
    main()