#!/usr/bin/env python
"""CourtIQ Master Database Seeding and Initialization CLI Script.

Applies all Alembic migrations and populates the database with demo fixtures
across all three platform domains: Competitions, Venues, and Rankings.

Usage:
    python scripts/seed_demo_data.py
"""

import sys
from pathlib import Path

# Add src to sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from courtiq.core.database import get_db
from courtiq.core.logging_config import setup_logging
from courtiq.ingestion.runner import IngestionRunner


def main() -> int:
    """Execute full database migration and multi-domain data seeding."""
    setup_logging(log_level="INFO")
    print("=" * 65)
    print("🎾 COURTIQ — MASTER DATABASE INITIALIZATION & SEEDING")
    print("=" * 65)

    db = get_db()
    runner = IngestionRunner(db)

    print("\n1. Applying Alembic database migrations up to head...")
    try:
        runner.run_migrations_if_needed()
        print("   ✓ Database migrations verified and applied.")
    except Exception as exc:
        print(f"   ✗ Migration error: {exc}")
        return 1

    print("\n2. Ingesting Competitions and Categories domain...")
    try:
        c_res = runner.ingest_competitions()
        print(f"   ✓ Competitions: {c_res.message}")
    except Exception as exc:
        print(f"   ✗ Competitions ingestion error: {exc}")
        return 1

    print("\n3. Ingesting Complexes and Venues domain...")
    try:
        v_res = runner.ingest_venues()
        print(f"   ✓ Venues: {v_res.message}")
    except Exception as exc:
        print(f"   ✗ Venues ingestion error: {exc}")
        return 1

    print("\n4. Ingesting Doubles Competitor Rankings domain...")
    try:
        r_res = runner.ingest_rankings()
        print(f"   ✓ Rankings: {r_res.message}")
    except Exception as exc:
        print(f"   ✗ Rankings ingestion error: {exc}")
        return 1

    print("\n" + "=" * 65)
    print("DATABASE VERIFICATION SUMMARY")
    print("=" * 65)
    tables = [
        "categories",
        "competitions",
        "complexes",
        "venues",
        "competitors",
        "competitor_rankings",
    ]
    all_ok = True
    for table in tables:
        try:
            count_res = db.fetch_one(f"SELECT COUNT(*) AS c FROM {table};")
            count = count_res["c"] if count_res else 0
            status = "✓ READY" if count > 0 else "⚠ EMPTY"
            print(f"  {table:<25} {count:>5} rows   [{status}]")
        except Exception as exc:
            print(f"  {table:<25} ERROR: {exc}")
            all_ok = False

    print("=" * 65)
    if all_ok:
        print("🚀 System fully initialized and ready! Run `streamlit run app.py`.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
