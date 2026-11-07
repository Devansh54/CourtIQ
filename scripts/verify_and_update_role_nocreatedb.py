"""Inspect and safely revoke CREATEDB from courtiq_migrator in running PostgreSQL 18."""

import os
import sys
import psycopg
from dotenv import load_dotenv

load_dotenv(".env")

su_pw = os.getenv("POSTGRES_SUPERUSER_PASSWORD")
mig_url = os.getenv("MIGRATION_DATABASE_URL").replace("postgresql+psycopg://", "postgresql://")
app_url = os.getenv("DATABASE_URL").replace("postgresql+psycopg://", "postgresql://")
test_url = os.getenv("TEST_DATABASE_URL").replace("postgresql+psycopg://", "postgresql://")

def main():
    print("=" * 65)
    print("COURTIQ — VERIFY AND UPDATE NOCREATEDB ROLE ATTRIBUTE")
    print("=" * 65)

    # 1. Connect as postgres superuser and inspect pg_roles
    with psycopg.connect(f"host=127.0.0.1 port=5432 dbname=postgres user=postgres password={su_pw}", autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT rolname, rolsuper, rolcreatedb, rolcanlogin
                FROM pg_roles
                WHERE rolname IN ('courtiq_migrator', 'courtiq_app')
                ORDER BY rolname;
            """)
            roles = cur.fetchall()
            print("Current role attributes:")
            for r in roles:
                print(f"  Role: {r[0]}, Superuser: {r[1]}, CreateDB: {r[2]}, Login: {r[3]}")

            # Revoke CREATEDB if currently set
            for r in roles:
                if r[0] == "courtiq_migrator" and r[2] is True:
                    print("\n[ACTION] Executing: ALTER ROLE courtiq_migrator NOCREATEDB;")
                    cur.execute("ALTER ROLE courtiq_migrator NOCREATEDB;")
                    print("[OK] Successfully revoked CREATEDB from courtiq_migrator.")

            # Re-verify
            cur.execute("""
                SELECT rolname, rolsuper, rolcreatedb, rolcanlogin
                FROM pg_roles
                WHERE rolname IN ('courtiq_migrator', 'courtiq_app')
                ORDER BY rolname;
            """)
            updated_roles = cur.fetchall()
            print("\nUpdated role attributes:")
            for r in updated_roles:
                print(f"  Role: {r[0]}, Superuser: {r[1]}, CreateDB: {r[2]}, Login: {r[3]}")
                assert r[1] is False, f"{r[0]} must not be superuser"
                assert r[2] is False, f"{r[0]} must NOT have CREATEDB"
            print("[PASS] Verified: Neither role has superuser or CREATEDB privileges.")

    # 2. Verify courtiq_migrator CANNOT create arbitrary new databases
    print("\n--- Testing Arbitrary Database Creation with courtiq_migrator ---")
    try:
        with psycopg.connect(mig_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE DATABASE arbitrary_security_test_db;")
                print("[FAIL] courtiq_migrator was able to create a database!")
                cur.execute("DROP DATABASE arbitrary_security_test_db;")
                return 1
    except psycopg.errors.InsufficientPrivilege as e:
        print(f"[PASS] Successfully blocked: {e.args[0].strip()}")
    except Exception as e:
        if "permission denied to create database" in str(e).lower():
            print(f"[PASS] Successfully blocked: {e}")
        else:
            print(f"[ERROR] Unexpected exception: {e}")
            return 1

    # 3. Verify courtiq_migrator CAN still execute DDL (CREATE, ALTER, DROP) in courtiq and courtiq_test
    print("\n--- Testing Schema DDL Privileges with courtiq_migrator ---")
    for db_conn_url, db_label in [(mig_url, "courtiq"), (test_url, "courtiq_test")]:
        with psycopg.connect(db_conn_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE TABLE IF NOT EXISTS public._ddl_test (id INT PRIMARY KEY);")
                cur.execute("ALTER TABLE public._ddl_test ADD COLUMN IF NOT EXISTS val TEXT;")
                cur.execute("DROP TABLE public._ddl_test;")
                print(f"[PASS] courtiq_migrator successfully executed DDL (CREATE, ALTER, DROP) on {db_label}.")

    # 4. Verify courtiq_app CANNOT execute DDL
    print("\n--- Testing DDL Denial with courtiq_app ---")
    try:
        with psycopg.connect(app_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE TABLE public._app_ddl_test (id INT);")
                print("[FAIL] courtiq_app was able to create a table!")
                return 1
    except psycopg.errors.InsufficientPrivilege as e:
        print(f"[PASS] DDL correctly denied for courtiq_app: {e.args[0].strip()}")

    # 5. Verify records preserved in courtiq
    print("\n--- Verifying Existing Data Preservation in courtiq ---")
    with psycopg.connect(app_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM categories;")
            cats = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM competitions;")
            comps = cur.fetchone()[0]
            print(f"Main database (courtiq): {cats} categories, {comps} competitions")
            assert cats == 5, f"Expected 5 categories, found {cats}"
            assert comps == 19, f"Expected 19 competitions, found {comps}"
            print("[PASS] Confirmed: 5 categories and 19 competitions intact.")

    print("\n" + "=" * 65)
    print("ALL NOCREATEDB ROLE AUDITS AND SECURITY CHECKS PASSED")
    print("=" * 65)
    return 0

if __name__ == "__main__":
    sys.exit(main())

