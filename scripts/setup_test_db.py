"""Provision courtiq_test database and configure permissions."""

import os
import psycopg
from dotenv import load_dotenv

load_dotenv(".env")
su_pw = os.getenv("POSTGRES_SUPERUSER_PASSWORD", "local_dev_superuser_password")

def main():
    try:
        with psycopg.connect(f"host=127.0.0.1 port=5432 dbname=postgres user=postgres password={su_pw}", autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = 'courtiq_test';")
                if not cur.fetchone():
                    cur.execute("CREATE DATABASE courtiq_test WITH ENCODING 'UTF8';")
                    print("Created courtiq_test database.")
                else:
                    print("courtiq_test already exists.")
                cur.execute("GRANT ALL PRIVILEGES ON DATABASE courtiq_test TO courtiq_migrator;")
                cur.execute("GRANT ALL PRIVILEGES ON DATABASE courtiq_test TO courtiq_app;")
                cur.execute("ALTER ROLE courtiq_migrator CREATEDB;")
                print("Granted privileges and CREATEDB to courtiq_migrator.")

        with psycopg.connect(f"host=127.0.0.1 port=5432 dbname=courtiq_test user=postgres password={su_pw}", autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("GRANT USAGE, CREATE ON SCHEMA public TO courtiq_migrator;")
                cur.execute("GRANT USAGE ON SCHEMA public TO courtiq_app;")
                cur.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO courtiq_migrator;")
                cur.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO courtiq_app;")
                cur.execute("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO courtiq_app;")
                cur.execute("ALTER DEFAULT PRIVILEGES FOR ROLE courtiq_migrator IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO courtiq_app;")
                cur.execute("ALTER DEFAULT PRIVILEGES FOR ROLE courtiq_migrator IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO courtiq_app;")
                print("Configured schema permissions on courtiq_test.")
    except Exception as e:
        print("Provisioning failed:", e)
        return 1
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

