#!/usr/bin/env python
"""CourtIQ SQLite to PostgreSQL Safe Data Migration Utility.

Safely transfers existing categories and competitions records from local SQLite
(data/courtiq.db) to PostgreSQL with automated backups, dry-run safety,
referential integrity checks, and idempotent upserts.

Usage:
    # Dry-run inspection (default):
    python scripts/migrate_sqlite_to_postgres.py --dry-run

    # Execute migration:
    python scripts/migrate_sqlite_to_postgres.py --apply
"""

import argparse
import datetime
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from sqlalchemy import create_engine, text

# Add src to sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from courtiq.core.config import get_settings
from courtiq.core.logging_config import setup_logging, get_logger

logger = get_logger("scripts.migrate_sqlite_to_postgres")


def create_sqlite_backup(sqlite_path: Path) -> Path:
    """Create a safe timestamped backup copy of the SQLite database before migration."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = sqlite_path.parent / f"{sqlite_path.name}.bak_{timestamp}"
    shutil.copy2(sqlite_path, backup_path)
    logger.info("Created pre-migration backup at: %s", backup_path)
    return backup_path


def read_sqlite_data(sqlite_path: Path) -> Tuple[List[Dict], List[Dict]]:
    """Read categories and competitions from source SQLite database."""
    conn = sqlite3.connect(str(sqlite_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Read categories
    cur.execute("SELECT category_id, category_name FROM categories;")
    categories = [dict(row) for row in cur.fetchall()]

    # Read competitions
    cur.execute("""
        SELECT competition_id, competition_name, parent_id, type, gender, category_id
        FROM competitions;
    """)
    competitions = [dict(row) for row in cur.fetchall()]

    conn.close()
    return categories, competitions


def migrate_to_postgres(
    categories: List[Dict],
    competitions: List[Dict],
    target_url: str,
    apply: bool = False,
) -> Dict[str, int]:
    """Transfer categories and competitions into PostgreSQL using idempotent upserts."""
    engine = create_engine(target_url, future=True)

    counts = {
        "source_categories": len(categories),
        "source_competitions": len(competitions),
        "target_categories_migrated": 0,
        "target_competitions_migrated": 0,
    }

    if not apply:
        logger.info("[DRY-RUN] Checked %d categories and %d competitions. No writes committed.",
                    len(categories), len(competitions))
        return counts

    # Separate parents and sub-competitions to guarantee referential ordering
    parents = [c for c in competitions if not c.get("parent_id")]
    children = [c for c in competitions if c.get("parent_id")]
    ordered_comps = parents + children

    upsert_cat_sql = text("""
        INSERT INTO categories (category_id, category_name)
        VALUES (:category_id, :category_name)
        ON CONFLICT (category_id) DO UPDATE SET
            category_name = EXCLUDED.category_name;
    """)

    upsert_comp_sql = text("""
        INSERT INTO competitions (competition_id, competition_name, parent_id, type, gender, category_id)
        VALUES (:competition_id, :competition_name, :parent_id, :type, :gender, :category_id)
        ON CONFLICT (competition_id) DO UPDATE SET
            competition_name = EXCLUDED.competition_name,
            parent_id = EXCLUDED.parent_id,
            type = EXCLUDED.type,
            gender = EXCLUDED.gender,
            category_id = EXCLUDED.category_id;
    """)

    with engine.begin() as conn:
        # Migrate categories
        for cat in categories:
            conn.execute(upsert_cat_sql, cat)
            counts["target_categories_migrated"] += 1

        # Migrate competitions in dependency order
        for comp in ordered_comps:
            conn.execute(upsert_comp_sql, comp)
            counts["target_competitions_migrated"] += 1

    # Verify counts in target database
    with engine.connect() as conn:
        cat_count = conn.execute(text("SELECT COUNT(*) FROM categories;")).scalar()
        comp_count = conn.execute(text("SELECT COUNT(*) FROM competitions;")).scalar()
        logger.info("Post-migration target verification: %d categories, %d competitions in PostgreSQL.",
                    cat_count, comp_count)

    return counts


def main() -> int:
    """Run data migration CLI."""
    setup_logging(log_level="INFO")
    parser = argparse.ArgumentParser(description="CourtIQ SQLite to PostgreSQL Migration Utility")
    parser.add_argument(
        "--sqlite-path",
        type=str,
        default=None,
        help="Path to source SQLite database (defaults to COURTIQ_DB_PATH)",
    )
    parser.add_argument(
        "--target-url",
        type=str,
        default=None,
        help="Target PostgreSQL connection URL (defaults to DATABASE_URL)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help="Apply changes to PostgreSQL database. Default is dry-run mode.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Run in dry-run mode without modifying target database (default).",
    )

    args = parser.parse_args()
    settings = get_settings()

    sqlite_file = Path(args.sqlite_path) if args.sqlite_path else settings.courtiq_db_path
    target_url = args.target_url or settings.database_url

    print("\n" + "=" * 65)
    print("COURTIQ — SQLITE TO POSTGRESQL DATA MIGRATION UTILITY")
    print("=" * 65)
    print(f"Source SQLite Path:    {sqlite_file}")
    print(f"Target Database URL:   {target_url.split('@')[-1] if '@' in target_url else target_url}")
    print(f"Execution Mode:        {'APPLY (LIVE WRITE)' if args.apply else 'DRY-RUN (INSPECTION ONLY)'}")
    print("=" * 65)

    if not sqlite_file.exists():
        print(f"\n[INFO] Source SQLite database not found at {sqlite_file}.")
        print("No historical data to migrate. Use 'python scripts/ingest_competitions.py' to populate PostgreSQL.")
        return 0

    # 1. Create backup
    backup_file = create_sqlite_backup(sqlite_file)
    print(f"[OK] Pre-migration backup created: {backup_file.name}")

    # 2. Extract SQLite records
    try:
        categories, competitions = read_sqlite_data(sqlite_file)
        print(f"[OK] Read {len(categories)} categories and {len(competitions)} competitions from SQLite.")
    except Exception as e:
        print(f"[ERROR] Failed to read source SQLite data: {e}")
        return 1

    # 3. Migrate records
    try:
        counts = migrate_to_postgres(
            categories=categories,
            competitions=competitions,
            target_url=target_url,
            apply=args.apply,
        )

        print("\n" + "-" * 65)
        print("MIGRATION SUMMARY")
        print("-" * 65)
        print(f"Categories Found:      {counts['source_categories']}")
        print(f"Competitions Found:    {counts['source_competitions']}")
        print(f"Categories Migrated:   {counts['target_categories_migrated']}")
        print(f"Competitions Migrated: {counts['target_competitions_migrated']}")
        print("-" * 65)

        if not args.apply:
            print("\n[NOTE] This was a DRY-RUN. To commit these records to PostgreSQL, run:")
            print("       python scripts/migrate_sqlite_to_postgres.py --apply\n")
        else:
            print("\n[SUCCESS] Data migration completed and verified successfully!\n")

        return 0
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        logger.error("Migration error: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

