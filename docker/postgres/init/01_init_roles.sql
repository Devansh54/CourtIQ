-- ==============================================================================
-- CourtIQ: PostgreSQL Role Provisioning & Security Initialization Script
-- Executed automatically on initial container startup via docker-entrypoint-initdb.d
-- ==============================================================================

-- 1. Read mandatory credentials from environment
\getenv migrator_pwd COURTIQ_MIGRATOR_PASSWORD
\getenv app_pwd COURTIQ_APP_PASSWORD

-- Verify passwords are provided
\if :{?migrator_pwd}
\else
  \echo 'ERROR: COURTIQ_MIGRATOR_PASSWORD environment variable is required!'
  \q 1
\endif

\if :{?app_pwd}
\else
  \echo 'ERROR: COURTIQ_APP_PASSWORD environment variable is required!'
  \q 1
\endif

-- 2. Ensure target databases exist (main courtiq and disposable courtiq_test)
SELECT 'CREATE DATABASE courtiq'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'courtiq')\gexec

SELECT 'CREATE DATABASE courtiq_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'courtiq_test')\gexec

-- 3. Provision Migration Role (DDL & Schema Management: CREATE, ALTER, DROP)
SELECT format('CREATE ROLE courtiq_migrator WITH LOGIN PASSWORD %L', :'migrator_pwd')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'courtiq_migrator')\gexec

SELECT format('ALTER ROLE courtiq_migrator WITH PASSWORD %L', :'migrator_pwd')\gexec

-- 4. Provision Application Runtime Role (DML Only: SELECT, INSERT, UPDATE, DELETE)
SELECT format('CREATE ROLE courtiq_app WITH LOGIN PASSWORD %L', :'app_pwd')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'courtiq_app')\gexec

SELECT format('ALTER ROLE courtiq_app WITH PASSWORD %L', :'app_pwd')\gexec

-- ==============================================================================
-- 5. Configure Main Application Database: courtiq
-- ==============================================================================
\c courtiq

GRANT CONNECT ON DATABASE courtiq TO courtiq_migrator;
GRANT CONNECT ON DATABASE courtiq TO courtiq_app;

GRANT USAGE, CREATE ON SCHEMA public TO courtiq_migrator;
GRANT USAGE ON SCHEMA public TO courtiq_app;

GRANT ALL ON ALL TABLES IN SCHEMA public TO courtiq_migrator;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO courtiq_migrator;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO courtiq_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO courtiq_app;

ALTER DEFAULT PRIVILEGES FOR ROLE courtiq_migrator IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO courtiq_app;

ALTER DEFAULT PRIVILEGES FOR ROLE courtiq_migrator IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO courtiq_app;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO courtiq_app;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO courtiq_app;

-- ==============================================================================
-- 6. Configure Disposable Test Database: courtiq_test
-- ==============================================================================
\c courtiq_test

GRANT CONNECT ON DATABASE courtiq_test TO courtiq_migrator;
GRANT CONNECT ON DATABASE courtiq_test TO courtiq_app;

GRANT USAGE, CREATE ON SCHEMA public TO courtiq_migrator;
GRANT USAGE ON SCHEMA public TO courtiq_app;

GRANT ALL ON ALL TABLES IN SCHEMA public TO courtiq_migrator;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO courtiq_migrator;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO courtiq_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO courtiq_app;

ALTER DEFAULT PRIVILEGES FOR ROLE courtiq_migrator IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO courtiq_app;

ALTER DEFAULT PRIVILEGES FOR ROLE courtiq_migrator IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO courtiq_app;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO courtiq_app;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO courtiq_app;
