-- ==============================================================================
-- CourtIQ: PostgreSQL Role Provisioning & Security Initialization Script
-- Executed automatically on initial container startup via docker-entrypoint-initdb.d
-- ==============================================================================

-- 1. Ensure target application database exists
SELECT 'CREATE DATABASE courtiq'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'courtiq')\gexec

-- Connect to courtiq database
\c courtiq

-- 2. Create Migration Role (DDL & Schema Management: CREATE, ALTER, DROP)
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'courtiq_migrator') THEN
      CREATE ROLE courtiq_migrator WITH LOGIN PASSWORD 'courtiq_migrator_password';
   END IF;
END
$do$;

-- 3. Create Application Runtime Role (DML Only: SELECT, INSERT, UPDATE, DELETE)
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'courtiq_app') THEN
      CREATE ROLE courtiq_app WITH LOGIN PASSWORD 'courtiq_app_password';
   END IF;
END
$do$;

-- 4. Grant Database Level Connection Rights
GRANT CONNECT ON DATABASE courtiq TO courtiq_migrator;
GRANT CONNECT ON DATABASE courtiq TO courtiq_app;

-- 5. Grant Schema Privileges on public schema
GRANT USAGE, CREATE ON SCHEMA public TO courtiq_migrator;
GRANT USAGE ON SCHEMA public TO courtiq_app;

-- 6. Grant Table Privileges to Application Role
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO courtiq_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO courtiq_app;

-- 7. Configure Default Privileges for Tables Created in Future by courtiq_migrator
ALTER DEFAULT PRIVILEGES FOR ROLE courtiq_migrator IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO courtiq_app;

ALTER DEFAULT PRIVILEGES FOR ROLE courtiq_migrator IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO courtiq_app;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO courtiq_app;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO courtiq_app;
