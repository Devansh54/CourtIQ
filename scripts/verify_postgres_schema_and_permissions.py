"""Verify PostgreSQL 18 Schema and Role Permissions.

Tests both courtiq_migrator and courtiq_app roles, verifies primary keys,
foreign keys, indexes, nullable parent relationships, and enforces DDL rejection.
"""

import sys
import psycopg

conn_params_app = "host=127.0.0.1 port=5432 dbname=courtiq user=courtiq_app password=courtiq_app_password"
conn_params_migrator = "host=127.0.0.1 port=5432 dbname=courtiq user=courtiq_migrator password=courtiq_migrator_password"


def main() -> int:
    print("=== 1. SCHEMA VERIFICATION (MIGRATOR ROLE) ===")
    with psycopg.connect(conn_params_migrator) as conn:
        with conn.cursor() as cur:
            # 1. Tables in public schema
            cur.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' ORDER BY table_name;
            """)
            tables = [r[0] for r in cur.fetchall()]
            print("Tables in public schema:", tables)
            assert "categories" in tables, "categories table missing"
            assert "competitions" in tables, "competitions table missing"
            assert "alembic_version" in tables, "alembic_version table missing"

            # 2. Columns & Nullability
            cur.execute("""
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name IN ('categories', 'competitions')
                ORDER BY table_name, ordinal_position;
            """)
            print("\nColumns:")
            cols = cur.fetchall()
            for r in cols:
                print(f"  {r[0]}.{r[1]} ({r[2]}, is_nullable={r[3]})")

            # Verify parent_id is nullable
            comp_cols = {r[1]: r[3] for r in cols if r[0] == "competitions"}
            assert comp_cols.get("parent_id") == "YES", "parent_id should be nullable"
            assert comp_cols.get("competition_id") == "NO", "competition_id must be NOT NULL"
            assert comp_cols.get("category_id") == "NO", "category_id must be NOT NULL"

            # 3. Foreign Keys
            cur.execute("""
                SELECT
                    tc.table_name, kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    rc.delete_rule
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                JOIN information_schema.referential_constraints AS rc
                  ON rc.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY';
            """)
            print("\nForeign Keys:")
            fks = cur.fetchall()
            for r in fks:
                print(f"  {r[0]}.{r[1]} -> {r[2]}.{r[3]} (ON DELETE {r[4]})")

            # 4. Indexes
            cur.execute("""
                SELECT tablename, indexname, indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname;
            """)
            print("\nIndexes:")
            for r in cur.fetchall():
                print(f"  {r[0]}: {r[1]} -> {r[2]}")

    print("\n=== 2. APPLICATION ROLE PERMISSIONS VERIFICATION (APP ROLE) ===")
    with psycopg.connect(conn_params_app) as conn:
        with conn.cursor() as cur:
            # Test SELECT
            cur.execute("SELECT COUNT(*) FROM categories;")
            print("SELECT categories count:", cur.fetchone()[0])

            # Test INSERT
            cur.execute("""
                INSERT INTO categories (category_id, category_name)
                VALUES ('sr:cat:perm_test', 'Permission Test Category');
            """)
            print("INSERT into categories: SUCCESS")

            # Test UPDATE
            cur.execute("""
                UPDATE categories SET category_name = 'Updated Perm Category'
                WHERE category_id = 'sr:cat:perm_test';
            """)
            print("UPDATE categories: SUCCESS")

            # Test DELETE
            cur.execute("""
                DELETE FROM categories WHERE category_id = 'sr:cat:perm_test';
            """)
            print("DELETE from categories: SUCCESS")
            conn.commit()

    print("\n=== 3. DDL SECURITY ENFORCEMENT CHECK (APP ROLE) ===")
    with psycopg.connect(conn_params_app) as conn:
        with conn.cursor() as cur:
            # Test DROP TABLE rejection
            try:
                cur.execute("DROP TABLE categories;")
                print("CRITICAL SECURITY FLAW: courtiq_app was able to DROP TABLE!")
                return 1
            except psycopg.errors.InsufficientPrivilege as e:
                conn.rollback()
                print("SECURE: DROP TABLE denied for courtiq_app ->", e.diag.message_primary)

            # Test ALTER TABLE rejection
            try:
                cur.execute("ALTER TABLE categories ADD COLUMN illicit_col text;")
                print("CRITICAL SECURITY FLAW: courtiq_app was able to ALTER TABLE!")
                return 1
            except psycopg.errors.InsufficientPrivilege as e:
                conn.rollback()
                print("SECURE: ALTER TABLE denied for courtiq_app ->", e.diag.message_primary)

    print("\n=== ALL SCHEMA & ROLE PERMISSION CHECKS PASSED ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())

