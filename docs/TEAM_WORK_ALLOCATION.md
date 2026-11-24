# CourtIQ — Team Domain Architecture & Module Ownership

**Product Name:** CourtIQ – Tennis Data & Analytics Explorer  
**System Architecture:** Modular Domain Relay Model  
**Version:** 1.0.0 (Production Release)  

---

## 1. Modular Domain Ownership Summary

The CourtIQ platform architecture is partitioned across three core domain modules, each owned by a dedicated engineer who developed the end-to-end data pipelines, relational storage schemas, analytical queries, and Streamlit user interfaces.

| Contributor | Title & Domain Ownership | Technical Scope & Deliverables | Status |
|---|---|---|:---:|
| **Devansh** | Project Architecture, Core Foundation & Competitions | Core infrastructure, PostgreSQL 18 migration, API client with strict dual modes, Alembic system, Competitions domain (7 SQL queries) | **Delivered & Merged** |
| **Mansi** | Complexes, Venues & Infrastructure Analytics | Alembic migration `0002_venues`, Complexes & Venues schemas, ETL pipeline, 7 SQL queries, Venues Explorer UI | **Delivered & Merged** |
| **Nilakshi** | Doubles Competitor Rankings & Integration | Alembic migrations `0003_rankings` & performance indexes, Rankings ETL, 6 SQL queries, Rankings Explorer UI, System Regression Test | **Delivered & Merged** |

---

## 2. Devansh — Project Architecture, Core Infrastructure & Competitions

### Scope & Responsibilities
Devansh established the foundational architecture and shared infrastructure for CourtIQ:
- **System Architecture & Design:** Layered modular architecture, multi-role PostgreSQL 18 security model (`courtiq_migrator` / `courtiq_app`), centralized Pydantic settings.
- **Shared Infrastructure (`src/courtiq/core/`):** Centralized logging, custom exception hierarchies, SQLAlchemy connection-pooled DatabaseManager, and rate-limited Sportradar API client with strict separation of `DEMO` and `LIVE` modes.
- **Competitions & Categories Domain:** Full ingestion pipeline, 7 analytical SQL queries, interactive hierarchy explorer, and Streamlit dashboard.
- **Testing & Verification:** Comprehensive unit and integration test framework, CI GitHub Actions configuration.

---

## 3. Mansi — Complexes & Venues Domain

### Scope & Responsibilities
Mansi built the Complexes & Venues domain adhering to the shared core standards:
- **Schema & Migrations:** Authored `0002_venues.py` creating the `complexes` and `venues` tables with foreign keys and compound unique constraints.
- **ETL Pipeline:** `VenuesExtractor` and `VenuesTransformer` validating and converting Sportradar complexes payloads into normalized records.
- **Repository & Analytics:** Idempotent upserts in `VenuesRepository`, 7 analytical SQL queries in `sql/queries/venues/`, and `VenuesAnalytics` summary KPIs.
- **Interactive UI:** Streamlit Venues Explorer (`pages/2_Venues.py`) with search, complex capacity analysis, and interactive query runner.

---

## 4. Nilakshi — Doubles Competitor Rankings & System Integration

### Scope & Responsibilities
Nilakshi delivered the Doubles Competitor Rankings domain and finalized full system release:
- **Schema & Performance:** Authored `0003_rankings.py`, `1c3add79e37f`, and `2a4b6c8d9e10_add_rankings_indexes.py` adding indexing on rankings and player profiles.
- **ETL Pipeline:** `RankingsExtractor` and `RankingsTransformer` processing world doubles rankings snapshots.
- **Repository & Analytics:** `RankingsRepository` supporting rankings snapshot replacements and 6 analytical SQL queries in `sql/queries/rankings/`.
- **Interactive UI:** Multi-tab Streamlit Rankings Explorer (`pages/3_Rankings.py`) with leaderboard, movement analysis, and interactive query execution.
- **Full System Regression:** Cross-domain pipeline regression test `tests/integration/test_full_system_regression.py`.
