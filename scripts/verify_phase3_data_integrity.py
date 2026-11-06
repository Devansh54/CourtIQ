"""CourtIQ Phase 3 Data Integrity & Parity Verification Script.

Compares source SQLite database records with target PostgreSQL 18.6 records:
- Exact row count verification (Categories: 5, Competitions: 19)
- Exact column-by-column content parity across all rows
- Referential integrity: all competition category_ids exist in categories
- Hierarchy integrity: all non-null parent_ids reference existing competitions
- Primary key uniqueness checks (no duplicate IDs)
"""

import os
import sys
import sqlite3
import psycopg
from dotenv import load_dotenv

load_dotenv(".env")

db_url = os.getenv("DATABASE_URL")
user_pass, host_db = db_url.split("@")
user = user_pass.split("//")[1].split(":")[0]
password = user_pass.split("//")[1].split(":")[1]
host_port, dbname = host_db.split("/")
host = host_port.split(":")[0]
port = int(host_port.split(":")[1])

conn_info = f"host={host} port={port} dbname={dbname} user={user} password={password}"

def main():
    print("=" * 65)
    print("COURTIQ — PHASE 3 DATA PARITY & INTEGRITY VERIFICATION")
    print("=" * 65)

    # 1. Read SQLite Source Data
    sqlite_conn = sqlite3.connect("data/courtiq.db")
    sqlite_conn.row_factory = sqlite3.Row
    s_cur = sqlite_conn.cursor()

    s_cur.execute("SELECT category_id, category_name FROM categories ORDER BY category_id;")
    sqlite_cats = [dict(r) for r in s_cur.fetchall()]

    s_cur.execute("""
        SELECT competition_id, competition_name, parent_id, type, gender, category_id
        FROM competitions ORDER BY competition_id;
    """)
    sqlite_comps = [dict(r) for r in s_cur.fetchall()]
    sqlite_conn.close()

    print(f"[SOURCE SQLite] Loaded {len(sqlite_cats)} categories, {len(sqlite_comps)} competitions.")

    # 2. Read PostgreSQL Destination Data
    with psycopg.connect(conn_info) as pg_conn:
        with pg_conn.cursor() as cur:
            # Identity confirmation
            cur.execute("SELECT version(), current_database(), current_user;")
            ver, db, usr = cur.fetchone()
            print(f"[DEST PostgreSQL] Database: {db}, User: {usr}")
            print(f"[DEST PostgreSQL] Engine:   {ver.split(',')[0]}")

            cur.execute("SELECT category_id, category_name FROM categories ORDER BY category_id;")
            pg_cats = [
                {"category_id": r[0], "category_name": r[1]}
                for r in cur.fetchall()
            ]

            cur.execute("""
                SELECT competition_id, competition_name, parent_id, type, gender, category_id
                FROM competitions ORDER BY competition_id;
            """)
            pg_comps = [
                {
                    "competition_id": r[0],
                    "competition_name": r[1],
                    "parent_id": r[2],
                    "type": r[3],
                    "gender": r[4],
                    "category_id": r[5],
                }
                for r in cur.fetchall()
            ]

            # 3. Row count checks
            print("\n--- 1. Record Count Checks ---")
            print(f"Categories count:   SQLite={len(sqlite_cats)} | PostgreSQL={len(pg_cats)}")
            assert len(pg_cats) == 5, f"Expected 5 categories, got {len(pg_cats)}"
            assert len(sqlite_cats) == len(pg_cats), "Category counts do not match"
            print("[PASS] Category count is exactly 5.")

            print(f"Competitions count: SQLite={len(sqlite_comps)} | PostgreSQL={len(pg_comps)}")
            assert len(pg_comps) == 19, f"Expected 19 competitions, got {len(pg_comps)}"
            assert len(sqlite_comps) == len(pg_comps), "Competition counts do not match"
            print("[PASS] Competition count is exactly 19.")

            # 4. Primary Key Uniqueness
            print("\n--- 2. Primary Key Uniqueness ---")
            cat_ids = [c["category_id"] for c in pg_cats]
            assert len(cat_ids) == len(set(cat_ids)), "Duplicate primary keys found in categories!"
            print(f"[PASS] All {len(cat_ids)} category primary keys are unique.")

            comp_ids = [c["competition_id"] for c in pg_comps]
            assert len(comp_ids) == len(set(comp_ids)), "Duplicate primary keys found in competitions!"
            print(f"[PASS] All {len(comp_ids)} competition primary keys are unique.")

            # 5. Referential Integrity (Category FK)
            print("\n--- 3. Foreign Key: Category References ---")
            cur.execute("""
                SELECT c.competition_id, c.category_id
                FROM competitions c
                LEFT JOIN categories cat ON c.category_id = cat.category_id
                WHERE cat.category_id IS NULL;
            """)
            orphan_cats = cur.fetchall()
            assert len(orphan_cats) == 0, f"Found orphan competitions with invalid category_id: {orphan_cats}"
            print("[PASS] All 19 competitions reference valid existing categories.")

            # 6. Referential Integrity (Parent Competition Self-Reference)
            print("\n--- 4. Foreign Key: Parent Hierarchy References ---")
            cur.execute("""
                SELECT c.competition_id, c.parent_id
                FROM competitions c
                LEFT JOIN competitions p ON c.parent_id = p.competition_id
                WHERE c.parent_id IS NOT NULL AND p.competition_id IS NULL;
            """)
            orphan_parents = cur.fetchall()
            assert len(orphan_parents) == 0, f"Found child competitions with invalid parent_id: {orphan_parents}"
            
            cur.execute("SELECT COUNT(*) FROM competitions WHERE parent_id IS NOT NULL;")
            child_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM competitions WHERE parent_id IS NULL;")
            parent_count = cur.fetchone()[0]
            print(f"[PASS] Top-level competitions: {parent_count}, Sub-competitions: {child_count}.")
            print("[PASS] All non-null parent_ids reference valid existing parent competitions.")

            # 7. Exact Data Parity Comparison
            print("\n--- 5. Source vs Destination Data Parity ---")
            # Compare categories
            cat_diffs = []
            pg_cats_by_id = {c["category_id"]: c for c in pg_cats}
            for s_cat in sqlite_cats:
                cid = s_cat["category_id"]
                if cid not in pg_cats_by_id:
                    cat_diffs.append(f"Missing category {cid} in PostgreSQL")
                elif s_cat != pg_cats_by_id[cid]:
                    cat_diffs.append(f"Mismatch in category {cid}: SQLite={s_cat} vs PG={pg_cats_by_id[cid]}")
            assert not cat_diffs, f"Category parity errors: {cat_diffs}"
            print(f"[PASS] All {len(sqlite_cats)} categories match byte-for-byte between SQLite and PostgreSQL.")

            # Compare competitions
            comp_diffs = []
            pg_comps_by_id = {c["competition_id"]: c for c in pg_comps}
            for s_comp in sqlite_comps:
                cid = s_comp["competition_id"]
                if cid not in pg_comps_by_id:
                    comp_diffs.append(f"Missing competition {cid} in PostgreSQL")
                else:
                    pg_c = pg_comps_by_id[cid]
                    for k in ["competition_id", "competition_name", "parent_id", "type", "gender", "category_id"]:
                        if s_comp[k] != pg_c[k]:
                            comp_diffs.append(f"Field mismatch in competition {cid}.{k}: SQLite='{s_comp[k]}' vs PG='{pg_c[k]}'")
            assert not comp_diffs, f"Competition parity errors: {comp_diffs}"
            print(f"[PASS] All {len(sqlite_comps)} competitions match byte-for-byte between SQLite and PostgreSQL.")

            # Print category summary
            print("\nMigrated Categories:")
            for c in pg_cats:
                cur.execute("SELECT COUNT(*) FROM competitions WHERE category_id = %s;", (c["category_id"],))
                cnt = cur.fetchone()[0]
                print(f"  - [{c['category_id']}] {c['category_name']} ({cnt} competitions)")

    print("\n" + "=" * 65)
    print("[PASS] ALL DATA INTEGRITY & PARITY CHECKS PASSED (100% PARITY)")
    print("=" * 65)
    return 0

if __name__ == "__main__":
    sys.exit(main())
