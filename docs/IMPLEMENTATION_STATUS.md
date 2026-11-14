# CourtIQ — Project Implementation Status & Tracking

**Product Name:** CourtIQ – Tennis Data & Analytics Explorer  
**Last Updated:** 2026-11-14  
**Current Milestone:** Milestone 1 & 2 Completed (Devansh 50% + Mansi 25% = 75%) | Ready for Milestone 3 (Nilakshi — 25%)  
**Lead Architect:** Devansh  
**Active Database Engine:** PostgreSQL 18 (via SQLAlchemy 2.x Core & Psycopg 3; SQLite retained for test fallback)  

---

## 1. Workload Completion Dashboard

| Contributor & Ownership | Planned Units | Completed Units | Progress (%) | Status |
|---|:---:|:---:|:---:|:---:|
| **Devansh** (Architecture, PostgreSQL Foundation, Competitions) | 50 | 50 | **100%** | **Completed & Merged** (PR #1, PR #2) |
| **Mansi** (Complexes & Venues Module) | 25 | 25 | **100%** | **Completed & Merged** (PR #3, PR #4) |
| **Nilakshi** (Doubles Rankings & Release Verification) | 25 | 0 | **0%** | Ready for Handoff 2 |
| **Total Product Workload** | **100** | **75** | **75%** | **Venues Milestone Complete** |

---

## 2. Devansh's Completed Implementation Checklist (50 / 50 Units)

### A. Repository & Architectural Foundations (12 Units)
- [x] Initial workspace audit and comprehensive project guide analysis.
- [x] Git repository initialization and remote configuration (`https://github.com/Devansh54/CourtIQ.git`).
- [x] Security setup: `.gitignore` and `.env.example` created.
- [x] Reference guide preserved in `docs/reference/PROJECT_GUIDE.pdf`.
- [x] Requirements Traceability Matrix (`docs/REQUIREMENTS.md`) covering all 56 requirements.
- [x] Team Work Allocation (`docs/TEAM_WORK_ALLOCATION.md`) establishing 50/25/25 model.
- [x] System Architecture (`docs/ARCHITECTURE.md`) with layered diagrams and sequences.
- [x] Database Architecture & ERD (`docs/DATABASE_DESIGN.md`) detailing all 6 tables.
- [x] API Documentation & Field Mappings (`docs/API_DOCUMENTATION.md`).
- [x] Relational Data Dictionary (`docs/DATA_DICTIONARY.md`).
- [x] Development Guidelines (`docs/DEVELOPMENT_GUIDELINES.md`).
- [x] Master README (`README.md`).

### B. Scalable PostgreSQL Database Architecture & Infrastructure (New Milestone)
- [x] Transitioned from single-threaded SQLite to **PostgreSQL 18** backed by **SQLAlchemy 2.x Core** and **Psycopg 3** (`psycopg[binary]>=3.1.18`).
- [x] Implemented connection pooling via SQLAlchemy `QueuePool` (`size=5`, `max_overflow=10`, `timeout=30s`, `pool_recycle=1800s`, `pool_pre_ping=True`).
- [x] Designed and deployed Docker Compose stack (`compose.yaml`) with `postgres:18-alpine`, persistent volume `postgres_data`, and healthchecks.
- [x] Provisioned least-privilege security roles via `docker/postgres/init/01_init_roles.sql`:
  - `courtiq_migrator`: Dedicated DDL role for migrations.
  - `courtiq_app`: Restricted DML role (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) without destructive DDL permissions.
- [x] Adopted **Alembic** (`alembic.ini`, `alembic/env.py`, `alembic/versions/0001_initial_competitions.py`) for deterministic, version-controlled schema migrations.
- [x] Created safe data migration script (`scripts/migrate_sqlite_to_postgres.py`):
  - Automatic timestamped backup (`data/courtiq.db.bak_<timestamp>`).
  - Safe `--dry-run` and `--apply` flags.
  - Foreign key referential order preservation.
  - Idempotent upserts (`ON CONFLICT (...) DO UPDATE`).
  - Post-migration count verification.
- [x] Authored complete PostgreSQL setup and operations guide (`docs/POSTGRESQL_SETUP.md`).
- [x] Configured GitHub Actions CI workflow (`.github/workflows/ci.yml`) with PostgreSQL 18 service container.

### C. Shared Core Infrastructure & Ingestion (14 Units)
- [x] Centralized configuration manager (`src/courtiq/core/config.py`) with PostgreSQL URL, migration URL, pooling settings, and operating modes (`LIVE`/`DEMO`).
- [x] Refactored `DatabaseManager` (`src/courtiq/core/database.py`) supporting connection pooling, ACID transaction contexts, named parameter queries (`:param`), DataFrame conversion, and Alembic runner.
- [x] Sportradar API client with rate limiting & exponential backoff (`src/courtiq/core/api_client.py`).
- [x] Domain-specific exception hierarchy (`src/courtiq/core/exceptions.py`).
- [x] Structured logging configuration (`src/courtiq/core/logging_config.py`).
- [x] Streamlit design system and utilities (`src/courtiq/utils/formatting.py`).

### D. Competitions & Categories Domain (16 Units)
- [x] Pydantic data models for Category and Competition (`schemas.py`).
- [x] Alembic migration revision (`alembic/versions/0001_initial_competitions.py`).
- [x] API Extractor (`extractor.py`).
- [x] JSON Transformer and normalizer (`transformer.py`).
- [x] Relational repository with all 7 required SQL queries updated for PostgreSQL named parameters (`repository.py`).
- [x] Individual query files in `sql/queries/competitions/` (Q1 through Q7).
- [x] Competitions analytics service (`analytics.py`).
- [x] Ingestion pipeline orchestrator (`src/courtiq/ingestion/runner.py`) & executable CLI (`scripts/ingest_competitions.py`).
- [x] Interactive Streamlit page (`pages/1_Competitions.py`) with telemetry in `app.py`.

### E. Testing & Quality Assurance (8 Units)
- [x] Core configuration and database unit tests (`tests/unit/test_config.py`, `tests/unit/test_database.py`).
- [x] Sportradar API client unit tests with rate limit verification.
- [x] Competitions extractor, transformer, and repository unit tests.
- [x] Mandated SQL queries verification test verifying all 7 competition queries.
- [x] End-to-end competitions pipeline integration test.
- [x] Multi-user concurrency test suite (`tests/concurrency/test_concurrency.py`) simulating concurrent dashboard traffic and isolated transactions without pool exhaustion.
- [x] **31 of 31 tests passing (100% pass rate).**

---

## 3. Mansi's Completed Implementation Checklist (25 / 25 Units)

### A. Database Migrations & Schemas (6 Units)
- [x] Authored Alembic migration `alembic/versions/0002_venues.py` creating `complexes` and `venues` tables with foreign keys and performance indexes.
- [x] Defined Pydantic schemas in `src/courtiq/domains/venues/schemas.py` for `Complex` and `Venue` with validation and string trimming.

### B. Extraction & Transformation Pipeline (6 Units)
- [x] Implemented `VenuesExtractor` in `src/courtiq/domains/venues/extractor.py` retrieving `complexes.json` with payload validation.
- [x] Implemented `VenuesTransformer` in `src/courtiq/domains/venues/transformer.py` transforming nested complexes and venues into validated model lists.

### C. Repository & Analytical SQL Queries (7 Units)
- [x] Built `VenuesRepository` in `src/courtiq/domains/venues/repository.py` with idempotent PostgreSQL upserts (`ON CONFLICT DO UPDATE`).
- [x] Implemented all 7 required analytical SQL queries in `sql/queries/venues/`:
  - `q1_venues_with_complex.sql`: Venues with complex details.
  - `q2_venues_count_per_complex.sql`: Aggregated venue count per complex.
  - `q3_venues_by_country.sql`: Venues filtered by country parameter.
  - `q4_venues_and_timezones.sql`: Venues mapped to timezones.
  - `q5_multi_venue_complexes.sql`: Complexes containing more than one venue.
  - `q6_venues_by_country_group.sql`: Venues grouped by country.
  - `q7_venues_for_specific_complex.sql`: Specific complex search with ANSI-compliant pattern matching.
- [x] Implemented domain analytics service `src/courtiq/domains/venues/analytics.py` generating summary KPIs and Plotly charts.

### D. Ingestion, UI & Test Suite (6 Units)
- [x] Integrated `ingest_venues()` into `src/courtiq/ingestion/runner.py` and created executable CLI `scripts/ingest_venues.py`.
- [x] Built interactive Streamlit dashboard `pages/2_Venues.py` with KPI cards, Plotly charts, interactive filters, CSV export, complex drilldown, and SQL Query Execution Center.
- [x] Delivered 38 unit tests in `tests/unit/venues/` covering schemas, extractor, transformer, repository, and analytics.
- [x] Created end-to-end integration test `tests/integration/test_venues_pipeline.py`.

---

## 4. Outstanding Work for Subsequent Contributors

### Milestone 3: Doubles Competitor Rankings & Integration (25 Effort Units)
- **Assignee:** Nilakshi (Rankings & Analytics Module Owner & Release Lead)
- **Status:** Ready to begin immediately.
- **Handoff Directive:** Detailed master instructions provided in `docs/handoffs/RANKINGS_MODULE_HANDOFF.md`.
- **Target Deliverables:**
  - Rankings domain extractor, transformer, repository, and analytics (`src/courtiq/domains/rankings/`)
  - All 6 mandated SQL queries in `sql/queries/rankings/`
  - Ingestion runner integration (`ingest_rankings()`) and CLI `scripts/ingest_rankings.py`
  - Interactive Streamlit Rankings Explorer (`pages/3_Rankings.py`)
  - Unit and integration tests in `tests/unit/rankings/` and `tests/integration/test_rankings_pipeline.py`
  - Final cross-domain integration, system regression, and product sign-off

---

## 5. Current Git State & Verification

- **Base Integration Branch:** `devansh-foundation-competitions`
- **Active Database Engine:** PostgreSQL 18 (`postgres:18-alpine` via Docker Compose).
- **Verified PRs Merged:**
  - PR #1: PostgreSQL Database Migration (Devansh) — Merged
  - PR #2: LIVE/DEMO API Enforcement & Audit (Devansh) — Merged
  - PR #3: Venues & Rankings Baseline Migrations (Mansi) — Merged
  - PR #4: Complete Venues & Complexes Module (Mansi) — Merged
- **CI / Build Status:** Green / Passing on GitHub Actions.
- **Total Test Suite:** 70 tests collected across core, competitions, venues, and concurrency.
