# DEVELOPER HANDOFF DIRECTIVE: VENUE & COMPLEXES MODULE OWNER

**To:** Mansi (Venue & Complexes Module Owner)  
**From:** Devansh (Lead Software Architect & Competitions Owner)  
**Project:** CourtIQ – Tennis Data & Analytics Explorer  
**Workload Allocation:** 25% Total Project Workload (25 Effort Units)  
**Parent Milestone:** Milestone 1 (Foundation, PostgreSQL 18 Architecture & Competitions — 50%) Completed & Verified  
**Target Milestone:** Milestone 2 (Complexes, Venues & Related Analytics — 25%)  
**Effective Date:** 2026-11-07  
**Target Base Branch for Pull Request:** `devansh-foundation-competitions`  

---

> [!IMPORTANT]
> **INSTRUCTIONS FOR THE RECIPIENT:**  
> Copy and paste the entire prompt below into your Antigravity conversation or development environment as your master instruction. Begin by inspecting the GitHub repository, verifying local tests, and reading the architectural documentation. Do NOT rewrite the shared core infrastructure established by Devansh. All code must target the merged PostgreSQL 18 foundation.

---

```markdown
# COURTIQ — MASTER IMPLEMENTATION DIRECTIVE: COMPLEXES & VENUES MODULE (25%)

## ROLE: VENUE & COMPLEXES MODULE OWNER & SENIOR DATA ENGINEER

You are **Mansi**, the **Venue & Complexes Module Owner** for **CourtIQ – Tennis Data & Analytics Explorer**, working alongside Devansh (Lead Architect & Competitions Owner) and Nilakshi (Rankings & Analytics Module Owner).

Devansh has already established and verified the entire project foundation (50% engineering workload): the repository structure, centralized configuration, Sportradar API client with strict dual-mode behavior (explicit DEMO fixtures vs. non-fallback LIVE API calls) and rate limiting, enterprise PostgreSQL 18 relational database engine with connection pooling (`QueuePool`), least-privilege security roles (`courtiq_migrator` / `courtiq_app`), version-controlled Alembic migrations, structured logging, custom exception hierarchies, shared Streamlit UI styling, and the complete Competitions & Categories domain (including all 7 mandated SQL queries, ETL pipeline, Streamlit explorer, and 31 passing unit, pipeline, and concurrency tests).

Your responsibility is to implement the complete **Complexes & Venues** domain (25% engineering workload), adhering strictly to the PostgreSQL 18 architecture, Alembic migration standards, and shared interfaces established by Devansh.

---

### 1. PROJECT IDENTITY & REPOSITORY OVERVIEW

- **Project Name:** CourtIQ
- **Full Title:** CourtIQ – Tennis Data & Analytics Explorer
- **Tagline:** Explore Competitions. Analyse Rankings. Discover Tennis.
- **GitHub Repository:** `https://github.com/Devansh54/CourtIQ`
- **Git Remote:** `https://github.com/Devansh54/CourtIQ.git`
- **Repository Visibility:** Private
- **Base Development Branch:** `devansh-foundation-competitions`
- **Feature Branch to Create:** `feature/venues-complexes`
- **Primary Technologies:** Python 3.12, Sportradar Tennis API v3, PostgreSQL 18 (`postgres:18-alpine`), SQLAlchemy 2.x Core, Psycopg 3 (`psycopg[binary]`), Alembic, Streamlit, Plotly, Pydantic v2
- **Team Workload Allocation:**
  - Devansh: Overall Architecture, PostgreSQL 18 Foundation, Core Infrastructure & Competitions (50%) [COMPLETED & MERGED]
  - Mansi: Complexes, Venues & Related Analytics (25%) [YOUR RESPONSIBILITY]
  - Nilakshi: Doubles Competitor Rankings, Integration & Final Release (25%) [SUBSEQUENT OWNER]

---

### 2. CORE ARCHITECTURE & CODEBASE STATUS YOU INHERIT

Begin your task by performing a workspace audit:
1. Verify that the PostgreSQL 18 container is running healthy:
   ```bash
   docker compose ps
   ```
2. Read `README.md` and all documentation in `docs/`:
   - `docs/PROJECT_OVERVIEW.md`: Business context and use cases.
   - `docs/REQUIREMENTS.md`: Requirements Traceability Matrix (`REQ-VEN-01` through `REQ-VEN-12`).
   - `docs/ARCHITECTURE.md`: Layered system architecture and sequence diagrams.
   - `docs/DATABASE_DESIGN.md`: Complete 6-table ER diagram and PostgreSQL 18 schema specifications.
   - `docs/POSTGRESQL_SETUP.md`: Database credentials, security roles, pooling parameters, and troubleshooting.
   - `docs/API_DOCUMENTATION.md`: Sportradar API endpoint mapping and mock fixtures.
   - `docs/DATA_DICTIONARY.md`: Column-level data definitions.
   - `docs/DEVELOPMENT_GUIDELINES.md`: Coding conventions, Git workflow, and branch rules.
   - `docs/TEAM_WORK_ALLOCATION.md`: 50/25/25 distribution and ownership boundaries.
3. Run the existing test suite:
   ```bash
   pytest tests -v
   ```
   Verify that all 31 existing tests pass (100% pass rate).

---

### 3. SHARED INTERFACES YOU MUST REUSE (DO NOT REWRITE OR OVERWRITE)

Devansh has built and tested reusable infrastructure in `src/courtiq/core/`. You must import and utilize these shared components rather than writing custom HTTP clients or database connections:

1. **Configuration (`src/courtiq/core/config.py`):**
   ```python
   from courtiq.core.config import get_settings
   settings = get_settings()
   ```
   Environment variables available:
   - `DATABASE_URL`: Runtime DML connection string (`courtiq_app`).
   - `MIGRATION_DATABASE_URL`: Administrative DDL connection string (`courtiq_migrator`).
   - `TEST_DATABASE_URL`: Automated test database connection string.
   - `COURTIQ_MODE`: `LIVE` or `DEMO`.

2. **Database Engine & Connection Pool (`src/courtiq/core/database.py`):**
   ```python
   from courtiq.core.database import get_db
   db = get_db()
   ```
   Methods to use:
   - `db.fetch_all(sql, params=None) -> List[Dict[str, Any]]`
   - `db.fetch_one(sql, params=None) -> Optional[Dict[str, Any]]`
   - `db.fetch_df(sql, params=None) -> pd.DataFrame`
   - `db.execute(sql, params=None) -> int`
   - `db.execute_many(sql, seq_of_params) -> int`
   - `with db.transaction() as conn:` context manager for atomic multi-statement operations.
   - **Parameter Binding:** Always use named parameter placeholders with `sqlalchemy.text` (e.g. `text("SELECT * FROM venues WHERE country_code = :country_code")` passing `{"country_code": "USA"}`). Never format or concatenate strings into queries.

3. **Sportradar API Client (`src/courtiq/core/api_client.py`):**
   ```python
   from courtiq.core.api_client import SportradarClient
   client = SportradarClient()
   payload = client.get("complexes.json")
   ```
   - In `DEMO` mode: returns synthetic fixture `tests/fixtures/complexes_sample.json` without making external network calls.
   - In `LIVE` mode: requires a valid `SPORTRADAR_API_KEY` and enforces a strict 1 RPS rate limit with exponential backoff. LIVE mode will **never** silently fall back to fixtures on API or network failure.

4. **Structured Logging (`src/courtiq/core/logging_config.py`):**
   ```python
   from courtiq.core.logging_config import get_logger
   logger = get_logger("domains.venues")
   ```

5. **Exceptions (`src/courtiq/core/exceptions.py`):**
   Use `DataValidationError`, `TransformationError`, `DatabaseError`, `APIError`, `ResourceNotFoundError`.

6. **UI Design System (`src/courtiq/utils/formatting.py`):**
   Use `apply_custom_css()`, `render_metric_card()`, `render_section_header()`.

---

### 4. YOUR EXACT DELIVERABLES (COMPLEXES & VENUES — 25%)

Official API Endpoint: `https://api.sportradar.com/tennis/trial/v3/en/complexes.json`  
Offline Test Fixture: `tests/fixtures/complexes_sample.json`

#### A. Alembic Database Migration: `alembic/versions/0002_venues.py`
Create the revision file chained to Devansh's baseline:
- `revision: str = '0002_venues'`
- `down_revision: Union[str, None] = '0001_initial_competitions'`
- Tables to create:
  1. **`complexes` Table:**
     - `complex_id` VARCHAR(50) PRIMARY KEY
     - `complex_name` VARCHAR(100) NOT NULL
  2. **`venues` Table:**
     - `venue_id` VARCHAR(50) PRIMARY KEY
     - `venue_name` VARCHAR(100) NOT NULL
     - `city_name` VARCHAR(100) NOT NULL
     - `country_name` VARCHAR(100) NOT NULL
     - `country_code` CHAR(3) NOT NULL
     - `timezone` VARCHAR(100) NOT NULL
     - `complex_id` VARCHAR(50) NOT NULL, FOREIGN KEY REFERENCES complexes(complex_id) ON DELETE CASCADE
  3. **Indexes:**
     - `idx_venues_complex_id` ON `venues(complex_id)`
     - `idx_venues_country_code` ON `venues(country_code)`
     - `idx_venues_city_name` ON `venues(city_name)`
- Test migration forward and rollback: `alembic upgrade head` and `alembic downgrade -1`.

#### B. API Extraction: `src/courtiq/domains/venues/extractor.py`
Implement `VenuesExtractor` to call `client.get("complexes.json")` and return the raw JSON dict.

#### C. Data Transformation: `src/courtiq/domains/venues/transformer.py`
Implement `VenuesTransformer`:
- Parse nested `complexes` array from Sportradar API payload.
- Extract `Complex` entities (`complex_id`, `complex_name`).
- Extract child `Venue` entities (`venue_id`, `venue_name`, `city_name`, `country_name`, `country_code`, `timezone`, `complex_id`).
- Validate data using `src/courtiq/domains/venues/schemas.py`.
- Return `Tuple[List[Complex], List[Venue]]`.

#### D. PostgreSQL Repository & Persistence: `src/courtiq/domains/venues/repository.py`
Implement `VenuesRepository`:
- `save_complexes(complexes: List[Complex]) -> int` using PostgreSQL idempotent upsert:
  ```sql
  INSERT INTO complexes (complex_id, complex_name)
  VALUES (:complex_id, :complex_name)
  ON CONFLICT (complex_id) DO UPDATE SET complex_name = EXCLUDED.complex_name;
  ```
- `save_venues(venues: List[Venue]) -> int` using PostgreSQL idempotent upsert:
  ```sql
  INSERT INTO venues (venue_id, venue_name, city_name, country_name, country_code, timezone, complex_id)
  VALUES (:venue_id, :venue_name, :city_name, :country_name, :country_code, :timezone, :complex_id)
  ON CONFLICT (venue_id) DO UPDATE SET
      venue_name = EXCLUDED.venue_name,
      city_name = EXCLUDED.city_name,
      country_name = EXCLUDED.country_name,
      country_code = EXCLUDED.country_code,
      timezone = EXCLUDED.timezone,
      complex_id = EXCLUDED.complex_id;
  ```
- Core count methods: `get_complex_count()`, `get_venue_count()`.
- Repository execution methods for all 7 required SQL queries.

#### E. Mandatory 7 SQL Query Files in `sql/queries/venues/`:
1. `q1_venues_with_complex.sql`: List all venues along with their associated complex name.
2. `q2_venues_count_per_complex.sql`: Count the number of venues in each complex.
3. `q3_venues_by_country.sql`: Get details of venues in a specific country (e.g., `:country_name` or 'Chile').
4. `q4_venues_and_timezones.sql`: Identify all venues and their timezones.
5. `q5_multi_venue_complexes.sql`: Find complexes that have more than one venue.
6. `q6_venues_by_country_group.sql`: List venues grouped by country.
7. `q7_venues_for_specific_complex.sql`: Find all venues for a specific complex (e.g., `:complex_pattern` or '%Nacional%').

#### F. Domain Analytics Service: `src/courtiq/domains/venues/analytics.py`
Implement `VenuesAnalytics` providing:
- High-level KPIs: Total Complexes, Total Venues, Countries Represented, Timezones Count, Multi-Venue Complexes Count.
- Plotly Visualizations:
  - Venues distribution by country (horizontal bar chart).
  - Timezone breakdown (pie or donut chart).
  - Complex-wise venue count comparison.

#### G. Ingestion Integration:
Add `ingest_venues()` to `src/courtiq/ingestion/runner.py` and create `scripts/ingest_venues.py`.

#### H. Streamlit Venues Explorer: `pages/2_Venues.py`
Replace the placeholder with a full-featured Streamlit page matching the design system of `pages/1_Competitions.py`:
- KPI metric cards across the top.
- Tab 1: Geographic & Timezone Analytics (Plotly charts).
- Tab 2: Complex Drilldown (venues per complex, multi-venue complexes).
- Tab 3: Interactive Filter & Search (country dropdown, timezone selector, text search).
- Tab 4: Required SQL Queries Execution Center (Q1 to Q7 interactive execution & raw SQL view).

#### I. Comprehensive Test Suite:
Create unit and integration tests:
- `tests/unit/venues/test_extractor.py`
- `tests/unit/venues/test_transformer.py`
- `tests/unit/venues/test_repository.py` (verifying all 7 SQL queries)
- `tests/integration/test_venues_pipeline.py`

---

### 5. MANDATORY SUBSEQUENT HANDOFF REQUIREMENT

Upon completing, testing, and verifying your 25% implementation:
1. Update `docs/IMPLEMENTATION_STATUS.md` reflecting your completed tasks.
2. Inspect the updated repository state.
3. Independently generate:
   `docs/handoffs/RANKINGS_MODULE_HANDOFF.md`
4. The handoff must be a complete, copy-paste-ready instruction prompt for **Nilakshi** (Rankings & Analytics Module Owner) describing Devansh's foundation, your completed venues module, step-by-step instructions for the Doubles Competitor Rankings domain, Alembic migration `0003_rankings.py`, and final regression testing.

---

### 6. GIT BRANCHING & OWNERSHIP RULES

1. Branch off: `devansh-foundation-competitions`.
2. Work on branch: `feature/venues-complexes`.
3. Open your Pull Request targeting base branch: `devansh-foundation-competitions`.
4. Do NOT edit `src/courtiq/core/` or `src/courtiq/domains/competitions/`.
5. Never use generic labels such as "Person 1/2/3" or "Developer 1/2/3" in code or documentation.
6. Commit your work with clear messages:
   - `feat(venues): add alembic migration 0002_venues`
   - `feat(venues): implement extractor, transformer and repository`
   - `feat(venues): implement 7 required sql queries and analytics`
   - `feat(venues): build interactive streamlit venues explorer`
   - `test(venues): add unit and integration test suite`
   - `docs(handoff): generate rankings module handoff prompt`
```
