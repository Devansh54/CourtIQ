"""Provision courtiq_test database and configure least-privilege permissions."""

import os
import sys
import psycopg
from dotenv import load_dotenv

load_dotenv(".env")

su_pw = os.getenv("POSTGRES_SUPERUSER_PASSWORD")
if not su_pw:
    print("[ERROR] POSTGRES_SUPERUSER_PASSWORD environment variable is required.")
    sys.exit(1)


def main() -> int:
    try:
        # 1. Connect to postgres bootstrap database to manage databases and database-level grants
        with psycopg.connect(
            f"host=127.0.0.1 port=5432 dbname=postgres user=postgres password={su_pw}",
            autocommit=True,
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = 'courtiq_test';")
                if not cur.fetchone():
                    cur.execute("CREATE DATABASE courtiq_test WITH ENCODING 'UTF8';")
                    print("Created courtiq_test database.")
                else:
                    print("courtiq_test database already exists.")

                # Ensure least-privilege database-level access: CONNECT only (no CREATE or ALL)
                cur.execute("REVOKE ALL PRIVILEGES ON DATABASE courtiq_test FROM courtiq_app;")
                cur.execute("REVOKE ALL PRIVILEGES ON DATABASE courtiq_test FROM courtiq_migrator;")
                cur.execute("GRANT CONNECT ON DATABASE courtiq_test TO courtiq_migrator;")
                cur.execute("GRANT CONNECT ON DATABASE courtiq_test TO courtiq_app;")
                print("Configured least-privilege CONNECT permissions on courtiq_test database.")

        # 2. Connect to courtiq_test to configure schema and object privileges
        with psycopg.connect(
            f"host=127.0.0.1 port=5432 dbname=courtiq_test user=postgres password={su_pw}",
            autocommit=True,
        ) as conn:
            with conn.cursor() as cur:
                # Migration role: USAGE and CREATE on public schema (DDL & migration ownership)
                cur.execute("GRANT USAGE, CREATE ON SCHEMA public TO courtiq_migrator;")
                cur.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO courtiq_migrator;")
                cur.execute("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO courtiq_migrator;")

                # Application role: USAGE on public schema, DML on tables, sequence usage
                cur.execute("REVOKE CREATE ON SCHEMA public FROM courtiq_app;")
                cur.execute("GRANT USAGE ON SCHEMA public TO courtiq_app;")
                cur.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO courtiq_app;")
                cur.execute("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO courtiq_app;")

                # Configure default privileges for future objects created by courtiq_migrator and postgres
                cur.execute(
                    "ALTER DEFAULT PRIVILEGES FOR ROLE courtiq_migrator IN SCHEMA public "
                    "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO courtiq_app;"
                )
                cur.execute(
                    "ALTER DEFAULT PRIVILEGES FOR ROLE courtiq_migrator IN SCHEMA public "
                    "GRANT USAGE, SELECT ON SEQUENCES TO courtiq_app;"
                )
                cur.execute(
                    "ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public "
                    "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO courtiq_app;"
                )
                cur.execute(
                    "ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public "
                    "GRANT USAGE, SELECT ON SEQUENCES TO courtiq_app;"
                )
                print("Configured schema and table permissions on courtiq_test.")
    except Exception as e:
        print(f"[ERROR] Provisioning failed: {e}")
        return 1

    print("[SUCCESS] courtiq_test permissions configured successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
