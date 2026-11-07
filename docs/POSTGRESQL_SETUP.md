# CourtIQ — PostgreSQL 18 Setup & Architecture Guide

## 1. Overview & Architectural Rationale

CourtIQ has transitioned to a **PostgreSQL-backed, multi-user-capable database foundation** powered by **PostgreSQL 18** (`postgres:18-alpine`).

While SQLite provided initial single-threaded prototyping, multi-user Streamlit dashboard interaction and analytical workloads require:
1. **True Concurrency & Connection Pooling:** Handled via SQLAlchemy 2.x `QueuePool` without SQLite write locks (`database is locked` errors).
2. **Strict Security & Role Separation:** DDL operations (table creation, schema evolution) are separated from runtime application queries (least-privilege DML).
3. **Structured Schema Versioning:** Managed through **Alembic**, enabling repeatable, transactional migrations across environments.
4. **ANSI SQL Compliance:** Standardized data types, constraints, and idempotent upserts (`ON CONFLICT (...) DO UPDATE`).

> **Note on SQLite:** SQLite is retained strictly as an offline fallback and for isolated in-memory/temporary unit test execution.

---

## 2. Security & Role Architecture

CourtIQ enforces database-level least-privilege access by splitting permissions across two dedicated roles:

| Role Name | Credential Source | Purpose | Privileges Granted |
|---|---|---|---|
| `courtiq_migrator` | `COURTIQ_MIGRATOR_PASSWORD` | Alembic migrations & initial DDL setup | `USAGE`, `CREATE` on schema `public`, table creation, altering, indexing. Owns migrations. |
| `courtiq_app` | `COURTIQ_APP_PASSWORD` | Streamlit runtime & ingestion pipelines | `SELECT`, `INSERT`, `UPDATE`, `DELETE` on tables; `USAGE`, `SELECT` on sequences. **Cannot execute DROP, ALTER, or TRUNCATE**. |

The administrative superuser (`postgres`) is configured via `POSTGRES_SUPERUSER_PASSWORD` and is used exclusively for bootstrapping the database instance and provisioning roles. Ordinary runtime operations and migrations never connect as superuser.

### Dual-Database Architecture
To ensure test isolation and prevent test pollution or accidental data deletion:
- **`courtiq`**: Main application database hosting migrated tournament records and live ingestion pipelines.
- **`courtiq_test`**: Dedicated, disposable test database provisioned for integration and concurrency test suites. Test cleanup operations execute solely against `courtiq_test`.

---

## 3. Quick Start with Docker Compose (Recommended)

Docker Compose provides a containerized setup for PostgreSQL 18 with automatic role provisioning and persistent volume storage.

### Prerequisites
- Docker Engine 24+ and Docker Compose v2+
- Windows users: Docker Desktop running

### Step 1: Configure Environment Variables
Copy `.env.example` to `.env` and specify mandatory secure credentials:

```bash
cp .env.example .env
```

Ensure the following mandatory credentials are set in `.env`:
```dotenv
POSTGRES_SUPERUSER_PASSWORD=your_secure_postgres_superuser_password_here
COURTIQ_MIGRATOR_PASSWORD=your_secure_migrator_password_here
COURTIQ_APP_PASSWORD=your_secure_app_password_here
```

### Step 2: Start the PostgreSQL Container
From the repository root:

```bash
docker compose up -d
```

This launches:
- **Service Name:** `db`
- **Image:** `postgres:18-alpine`
- **Container Name:** `courtiq_postgres`
- **Host Port Binding:** `127.0.0.1:5432:5432` (IPv4 localhost to avoid Windows IPv6 socket latency)
- **Initialization Script:** `docker/postgres/init/01_init_roles.sql` executes automatically on initial volume creation, provisioning `courtiq`, `courtiq_test`, roles, and grants using environment variables.
- **Volume:** `postgres_data` mounted to `/var/lib/postgresql` (enclosing PostgreSQL 18 PGDATA directory `/var/lib/postgresql/18/docker`).

### Step 3: Verify Container Health
```bash
docker compose ps
```
The status should indicate `Up (healthy)`.

To view container logs:
```bash
docker compose logs -f db
```

---

## 4. Manual / Native PostgreSQL 18 Setup

If running a local native PostgreSQL 18 instance instead of Docker:

### Step 1: Install PostgreSQL 18
- **Ubuntu/Debian:** Install PostgreSQL 18 via official PGDG apt repository.
- **macOS:** `brew install postgresql@18`
- **Windows:** Download and install PostgreSQL 18 from [PostgreSQL Official Installer](https://www.postgresql.org/download/windows/).

### Step 2: Provision Databases and Roles
Execute the initialization script using `psql` as the `postgres` superuser, passing role passwords as environment variables:

```bash
COURTIQ_MIGRATOR_PASSWORD="your_secure_migrator_password" COURTIQ_APP_PASSWORD="your_secure_app_password" psql -U postgres -h 127.0.0.1 -f docker/postgres/init/01_init_roles.sql
```

---

## 5. Environment Configuration

Ensure your `.env` contains the standardized connection strings using IPv4 `127.0.0.1`:

```dotenv
# ==============================================================================
# Database Configuration (PostgreSQL 18)
# ==============================================================================
# Mandatory Credentials
POSTGRES_SUPERUSER_PASSWORD=your_secure_postgres_superuser_password_here
COURTIQ_MIGRATOR_PASSWORD=your_secure_migrator_password_here
COURTIQ_APP_PASSWORD=your_secure_app_password_here

# Runtime Application Connection (Least-privilege DML role)
DATABASE_URL=postgresql+psycopg://courtiq_app:your_secure_app_password_here@127.0.0.1:5432/courtiq

# Database Migration Connection (Dedicated DDL role)
MIGRATION_DATABASE_URL=postgresql+psycopg://courtiq_migrator:your_secure_migrator_password_here@127.0.0.1:5432/courtiq

# Disposable Automated Test Database URL (Used by Pytest)
TEST_DATABASE_URL=postgresql+psycopg://courtiq_migrator:your_secure_migrator_password_here@127.0.0.1:5432/courtiq_test

# Concurrency Connection Pooling Settings (SQLAlchemy QueuePool)
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800
DB_POOL_PRE_PING=true
```

---

## 6. Running Alembic Database Migrations

Apply the database schema revisions using Alembic (runs via `MIGRATION_DATABASE_URL` as `courtiq_migrator`):

```bash
# Upgrade main database schema to latest revision (head)
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
- **Referential Integrity Ordering:** Inserts categories first, followed by top-level competitions, then sub-competitions.
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
=================================================================
COURTIQ — SQLITE TO POSTGRESQL DATA MIGRATION UTILITY
=================================================================
Source SQLite Path:    data/courtiq.db
Target Database URL:   127.0.0.1:5432/courtiq
Execution Mode:        APPLY (LIVE WRITE)
=================================================================
[OK] Pre-migration backup created: data/courtiq.db.bak_20261106_141111
[OK] Read 5 categories and 19 competitions from SQLite.
[SUCCESS] Post-migration target verification: 5 categories, 19 competitions in PostgreSQL.
```

---

## 8. Verifying the Setup

### Run Automated Unit and Concurrency Tests
Ensure all 22 tests pass against the new database layer:

```bash
pytest tests -v --durations=10
```

- **Unit tests** execute against isolated SQLite or PostgreSQL test databases.
- **Integration & Concurrency tests** require `TEST_DATABASE_URL` pointing to `courtiq_test` on `127.0.0.1:5432`. They will never silently fall back to SQLite.

### Run Streamlit Application
```bash
streamlit run app.py
```
Check the **Technical Architecture & System Telemetry** card on the homepage to verify:
- **Relational Database:** `PostgreSQL 18 (Multi-User Foundation)`
- **Database Dialect:** `postgresql`
- **Pool Configuration:** `size=5, max_overflow=10, timeout=30s`

---

## 9. Troubleshooting & FAQ

### Issue: `psycopg.OperationalError: connection failed: Connection refused`
- **Cause:** PostgreSQL container is not running or port 5432 is not exposed.
- **Solution:** Verify container status with `docker compose ps`. Restart with `docker compose up -d`.

### Issue: `permission denied for table ...`
- **Cause:** Application connected with `courtiq_app`, but tables were created without proper default privileges.
- **Solution:** Re-run the role grant script:
  ```bash
  psql -h 127.0.0.1 -U postgres -d courtiq -f docker/postgres/init/01_init_roles.sql
  ```

### Issue: `MIGRATION_DATABASE_URL is not configured`
- **Cause:** Attempting to run migrations without specifying `MIGRATION_DATABASE_URL`.
- **Solution:** Set `MIGRATION_DATABASE_URL` in `.env` identifying the `courtiq_migrator` role. CourtIQ refuses to run migrations using runtime application credentials.

### Issue: Port 5432 collision
- **Cause:** Another local PostgreSQL instance is already bound to port 5432.
- **Solution:** In `compose.yaml`, map to an alternative host port such as `5433:5432`, and update your `.env` connection strings to port `5433`.
