"""CourtIQ Phase 3 Pre-migration Verification Script.

Inspects main PostgreSQL database 'courtiq', table schemas, constraints,
current record counts, and verifies SQLite source and backup files.
"""

import os
import sys
from pathlib import Path
import psycopg
from dotenv import load_dotenv

load_dotenv(".env")

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("[ERROR] DATABASE_URL not set in .env")
    sys.exit(1)

# Extract connection parameters from psycopg/SQLAlchemy URL
user_pass, host_db = db_url.split("@")
user = user_pass.split("//")[1].split(":")[0]
password = user_pass.split("//")[1].split(":")[1]
host_port, dbname = host_db.split("/")
host = host_port.split(":")[0]
port = int(host_port.split(":")[1])

conn_info = f"host={host} port={port} dbname={dbname} user={user} password={password}"

def main():
    print("=" * 65)
    print("COURTIQ — PHASE 3 PRE-MIGRATION VERIFICATION")
    print("=" * 65)

    # 1. Verify SQLite files
    sqlite_path = Path("data/courtiq.db")
    backup_path = Path("data/courtiq.db.bak_20261106_135605")

    print("\n--- 1. SQLite Source & Backup Verification ---")
    if not sqlite_path.exists():
        print(f"[FAIL] Source SQLite file missing at {sqlite_path}")
        return 1
    print(f"[PASS] Source SQLite file exists: {sqlite_path} ({sqlite_path.stat().st_size} bytes)")

    if not backup_path.exists():
        print(f"[FAIL] Backup SQLite file missing at {backup_path}")
        return 1
    print(f"[PASS] Backup SQLite file exists: {backup_path} ({backup_path.stat().st_size} bytes)")

    # 2. Verify PostgreSQL connection & identity
    print("\n--- 2. PostgreSQL Connection & Identity ---")
    try:
        with psycopg.connect(conn_info) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                print(f"[PASS] Connected to PostgreSQL version: {version.split(',')[0]}")

                cur.execute("SELECT current_database(), current_user;")
                db, usr = cur.fetchone()
                print(f"[PASS] Current database: {db}")
                print(f"[PASS] Current user:     {usr}")
                assert db == "courtiq", f"Expected db 'courtiq', got '{db}'"
                assert usr == "courtiq_app", f"Expected user 'courtiq_app', got '{usr}'"

                # 3. Verify Alembic migration status
                print("\n--- 3. Alembic Migration Status ---")
                cur.execute("SELECT version_num FROM alembic_version;")
                revisions = cur.fetchall()
                print(f"[PASS] Current alembic_version: {[r[0] for r in revisions]}")
                assert any("0001" in r[0] for r in revisions), "0001_initial_competitions missing!"

                # 4. Verify Tables & Constraints
                print("\n--- 4. Schema, Constraints & Indexes ---")
                cur.execute("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public' ORDER BY table_name;
                """)
                tables = [r[0] for r in cur.fetchall()]
                print(f"[PASS] Tables found: {tables}")
                assert "categories" in tables, "categories table missing"
                assert "competitions" in tables, "competitions table missing"

                # Check constraints via pg_constraint
                cur.execute("""
                    SELECT conrelid::regclass::text, conname, contype, pg_get_constraintdef(oid)
                    FROM pg_constraint
                    WHERE conrelid IN ('categories'::regclass, 'competitions'::regclass)
                    ORDER BY conrelid::regclass::text, contype;
                """)
                constraints = cur.fetchall()
                print("Constraints:")
                pk_count = 0
                fk_count = 0
                for c in constraints:
                    print(f"  {c[0]}.{c[1]} (type={c[2]}): {c[3]}")
                    if c[2] == 'p':
                        pk_count += 1
                    elif c[2] == 'f':
                        fk_count += 1
                assert pk_count >= 2, f"Expected 2 PKs, found {pk_count}"
                assert fk_count >= 2, f"Expected 2 FKs, found {fk_count}"

                # Check indexes
                cur.execute("""
                    SELECT tablename, indexname, indexdef FROM pg_indexes
                    WHERE schemaname = 'public' ORDER BY tablename, indexname;
                """)
                indexes = cur.fetchall()
                print("Indexes:")
                for idx in indexes:
                    print(f"  {idx[0]}.{idx[1]}: {idx[2]}")

                # 5. Check destination table contents
                print("\n--- 5. Current Destination Table Records ---")
                cur.execute("SELECT COUNT(*) FROM categories;")
                cat_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM competitions;")
                comp_count = cur.fetchone()[0]
                print(f"Current destination records in 'courtiq':")
                print(f"  categories:   {cat_count}")
                print(f"  competitions: {comp_count}")

    except Exception as e:
        print(f"[ERROR] Database inspection failed: {e}")
        return 1

    print("\n" + "=" * 65)
    print("[PASS] ALL PRE-MIGRATION CHECKS COMPLETED SUCCESSFULLY")
    print("=" * 65)
    return 0

if __name__ == "__main__":
    sys.exit(main())
