#!/usr/bin/env python
"""CourtIQ Competitions Ingestion Executable CLI Script.

Run this script to apply migrations and ingest competitions and categories
from the Sportradar Tennis API or offline mock fixtures into the relational database.

Usage:
    python scripts/ingest_competitions.py
"""

import sys
from pathlib import Path

# Add src to sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from courtiq.core.logging_config import setup_logging
from courtiq.ingestion.runner import IngestionRunner


def main() -> int:
    """Run competitions ingestion CLI."""
    setup_logging(log_level="INFO")
    runner = IngestionRunner()
    result = runner.ingest_competitions()

    print("\n" + "=" * 60)
    print("COURTIQ — COMPETITIONS INGESTION EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Domain:                {result.domain}")
    print(f"Status:                {result.status}")
    print(f"Categories Ingested:   {result.categories_ingested}")
    print(f"Competitions Ingested: {result.competitions_ingested}")
    print(f"Total Records:         {result.records_ingested}")
    print(f"Errors:                {result.errors}")
    print(f"Message:               {result.message}")
    print("=" * 60 + "\n")

    return 0 if result.status == "SUCCESS" else 1


if __name__ == "__main__":
    sys.exit(main())
