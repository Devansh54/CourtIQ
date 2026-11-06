# CourtIQ — PostgreSQL Setup & Migration Guide

## 1. Overview & Architectural Rationale

CourtIQ uses **PostgreSQL 16+** as its primary production and evaluation database engine. 

While SQLite provided initial single-threaded prototyping, multi-user Streamlit dashboard interaction and analytical workloads require:
1. **True Concurrency & Connection Pooling:** Handled via SQLAlchemy 2.x `QueuePool` without SQLite write locks (`database is locked` errors).
2. **Strict Security & Role Separation:** DDL operations (table creation, schema evolution) are separated from runtime application queries (least-privilege DML).
3. **Structured Schema Versioning:** Managed through **Alembic**, enabling repeatable, transactional migrations across environments.
4. **ANSI SQL Compliance:** Standardized data types, constraints, and idempotent upserts (`ON CONFLICT (...) DO UPDATE`).

> **Note on SQLite:** SQLite is retained strictly as an offline fallback and for isolated in-memory/temporary unit test execution.

---

## 2. Security & Role Architecture

CourtIQ enforces database-level least-privilege access by splitting permissions across two dedicated roles:

| Role Name | Default Credentials | Purpose | Privileges Granted |
|---|---|---|---|
| `courtiq_migrator` | `courtiq_migrator_password` | Alembic migrations & initial DDL setup | `ALL PRIVILEGES` on schema `public`, table creation, altering, indexing. |
| `courtiq_app` | `courtiq_app_password` | Streamlit runtime & ingestion pipelines | `SELECT`, `INSERT`, `UPDATE`, `DELETE` on tables; `USAGE`, `SELECT` on sequences. **Cannot execute DROP or ALTER**. |

The administrative superuser (`postgres`) is used exclusively for provisioning database instances and creating roles.

---

## 3. Quick Start with Docker Compose (Recommended)

Docker Compose provides a single-command setup for PostgreSQL 16 with automatic role provisioning and persistent volume storage.

### Prerequisites
- Docker Engine 24+ and Docker Compose v2+
- Windows users: Docker Desktop running

### Step 1: Start the PostgreSQL Container
From the repository root:

```bash
docker compose up -d
```

This launches:
- **Image:** `postgres:18-alpine`
- **Container Name:** `courtiq_postgres`
- **Host Port Binding:** `127.0.0.1:5432:5432`
- **Initialization Script:** `docker/postgres/init/01_init_roles.sql` executes automatically on first start, creating the `courtiq` database, roles, and grants.
- **Volume:** `postgres_data` (persisted on disk).

### Step 2: Verify Container Health
```bash
docker compose ps
```
The status should indicate `Up (healthy)`.

To view container logs:
```bash
docker compose logs -f postgres
```

---

## 4. Manual / Native PostgreSQL Setup

If you prefer running a local native PostgreSQL instance instead of Docker:

### Step 1: Install PostgreSQL 16+
- **Ubuntu/Debian:** `sudo apt install postgresql-16`
- **macOS:** `brew install postgresql@16`
- **Windows:** Download and install from [PostgreSQL Official Installer](https://www.postgresql.org/download/windows/).

### Step 2: Provision Database and Roles
Execute the initialization script using `psql` as the `postgres` superuser:

```bash
psql -U postgres -h localhost -f docker/postgres/init/01_init_roles.sql
```

Alternatively, run the SQL commands manually in a `psql` session:

```sql
-- Create database
CREATE DATABASE courtiq WITH ENCODING 'UTF8';

\c courtiq;

-- Create migration role
CREATE USER courtiq_migrator WITH PASSWORD 'courtiq_migrator_password';
GRANT ALL PRIVILEGES ON DATABASE courtiq TO courtiq_migrator;
GRANT ALL ON SCHEMA public TO courtiq_migrator;

-- Create application role
CREATE USER courtiq_app WITH PASSWORD 'courtiq_app_password';
GRANT CONNECT ON DATABASE courtiq TO courtiq_app;
GRANT USAGE ON SCHEMA public TO courtiq_app;

-- Grant DML permissions
ALTER DEFAULT PRIVILEGES FOR ROLE courtiq_migrator IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO courtiq_app;
ALTER DEFAULT PRIVILEGES FOR ROLE courtiq_migrator IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO courtiq_app;
```

---

## 5. Environment Configuration

Copy `.env.example` to `.env` if not already created:

```bash
cp .env.example .env
```

Ensure your `.env` contains the PostgreSQL connection strings:

```dotenv
# ==============================================================================
# Database Configuration (PostgreSQL 16+)
# ==============================================================================
# Runtime application connection (Least-privilege DML role)
DATABASE_URL=postgresql+psycopg://courtiq_app:courtiq_app_password@localhost:5432/courtiq

# Alembic migrations & schema evolution (DDL role)
MIGRATION_DATABASE_URL=postgresql+psycopg://courtiq_migrator:courtiq_migrator_password@localhost:5432/courtiq

# Concurrency Connection Pooling Settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800
DB_POOL_PRE_PING=true
```

---

## 6. Running Alembic Database Migrations

Apply the database schema revisions using Alembic:

```bash
# Upgrade database schema to the latest revision (head)
alembic upgrade head
```

### Inspecting Migration Status
```bash
# Check current migration revision applied to database
alembic current

# View full migration revision history
alembic history --verbose
```

---

## 7. Migrating Data from SQLite to PostgreSQL

If you have existing historical data in `data/courtiq.db`, transfer it to PostgreSQL using the automated migration script.

### Features of the Migration Script
- **Automatic Backup:** Creates a timestamped `.bak_<timestamp>` copy of `data/courtiq.db` before touching any data.
- **Dry-Run Safe Mode:** Runs in `--dry-run` mode by default, counting rows and validating connections without modifying PostgreSQL.
- **Referential Integrity Ordering:** Inserts parent categories first, followed by top-level competitions, then sub-competitions.
- **Idempotency:** Employs `ON CONFLICT (...) DO UPDATE` to prevent primary key collisions.
- **Audit Verification:** Verifies row counts between SQLite source and PostgreSQL target.

### Step 1: Perform a Dry Run
```bash
python scripts/migrate_sqlite_to_postgres.py --dry-run
```

### Step 2: Apply the Migration
```bash
python scripts/migrate_sqlite_to_postgres.py --apply
```

Example output:
```text
[INFO] Source SQLite: data/courtiq.db
[INFO] Target PostgreSQL: localhost:5432/courtiq
[INFO] Created SQLite backup: data/courtiq.db.bak_20261106_090500
[INFO] Migrated 5 categories successfully.
[INFO] Migrated 19 competitions successfully.
[INFO] Verification: categories (SQLite: 5, PG: 5) - MATCH
[INFO] Verification: competitions (SQLite: 19, PG: 19) - MATCH
[SUCCESS] Migration finished with 0 errors.
```

---

## 8. Verifying the Setup

### Run Automated Unit and Concurrency Tests
Ensure all 22 tests pass against the new database layer:

```bash
pytest tests -v
```

To run tests directly against PostgreSQL:
```bash
TEST_DATABASE_URL=postgresql+psycopg://courtiq_migrator:courtiq_migrator_password@localhost:5432/courtiq pytest tests -v
```

### Run Streamlit Application
```bash
streamlit run app.py
```
Check the **Technical Architecture & System Telemetry** card on the homepage to verify:
- **Relational Database:** `PostgreSQL 16+ (Primary Production Engine)`
- **Database Dialect:** `postgresql`
- **Pool Configuration:** `size=5, max_overflow=10, timeout=30s`

---

## 9. Troubleshooting & FAQ

### Issue: `psycopg.OperationalError: connection failed: Connection refused`
- **Cause:** PostgreSQL service is not running or port 5432 is not exposed.
- **Solution:** Verify container status with `docker compose ps`. If stopped, restart with `docker compose up -d`.

### Issue: `permission denied for table ...`
- **Cause:** Application connected with `courtiq_app`, but tables were created by another user without granting DML privileges.
- **Solution:** Re-run the role grant script:
  ```bash
  psql -h localhost -U postgres -d courtiq -f docker/postgres/init/01_init_roles.sql
  ```

### Issue: `alembic: command not found`
- **Cause:** Virtual environment is not activated or dependencies are missing.
- **Solution:** Activate your virtual environment and run `pip install -r requirements.txt`.

### Issue: Port 5432 collision
- **Cause:** Another local PostgreSQL instance is already bound to port 5432.
- **Solution:** In `compose.yaml`, map to an alternative host port such as `5433:5432`, and update your `DATABASE_URL` port to `5433`.

