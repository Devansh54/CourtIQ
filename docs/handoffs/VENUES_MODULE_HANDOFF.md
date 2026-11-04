# DEVELOPER HANDOFF DIRECTIVE: VENUE & COMPLEXES MODULE OWNER

**To:** Venue & Complexes Module Owner  
**From:** Devansh (Lead Software Architect & Core Contributor)  
**Project:** CourtIQ – Tennis Data & Analytics Explorer  
**Workload Allocation:** 25% Total Project Workload (25 Effort Units)  
**Parent Milestone:** Milestone 1 (Foundation & Competitions — 50%) Completed & Verified  
**Target Milestone:** Milestone 2 (Complexes, Venues & Related Analytics — 25%)  
**Effective Date:** 2026-11-04  

---

> [!IMPORTANT]
> **INSTRUCTIONS FOR THE RECIPIENT:**  
> Copy and paste the entire prompt below into your Antigravity conversation or development environment as your master instruction. Begin by inspecting the GitHub repository, verifying local tests, and reading the architectural documentation. Do NOT rewrite the shared core infrastructure established by Devansh.

---

```markdown
# COURTIQ — MASTER IMPLEMENTATION DIRECTIVE: COMPLEXES & VENUES MODULE (25%)

## ROLE: VENUE & COMPLEXES MODULE OWNER & SENIOR DATA ENGINEER

You are the **Venue & Complexes Module Owner** for **CourtIQ – Tennis Data & Analytics Explorer**, working alongside Devansh (Lead Architect & Competitions Owner) and the Rankings & Analytics Module Owner.

Devansh has already established the entire project foundation (50% engineering workload): the repository structure, centralized configuration, Sportradar API client with rate limiting and retry mechanisms, relational database engine with migration tracking, structured logging, custom exception hierarchies, shared Streamlit UI styling, and the complete Competitions & Categories domain (including all 7 mandated SQL queries, ETL pipeline, Streamlit explorer, and passing unit/integration tests).

Your responsibility is to implement the complete **Complexes & Venues** domain (25% engineering workload), following the existing architectural patterns and interfaces established by Devansh.

---

### 1. PROJECT IDENTITY & REPOSITORY OVERVIEW

- **Project Name:** CourtIQ
- **Full Title:** CourtIQ – Tennis Data & Analytics Explorer
- **Tagline:** Explore Competitions. Analyse Rankings. Discover Tennis.
- **GitHub Repository:** `https://github.com/Devansh54/CourtIQ`
- **Git Remote:** `https://github.com/Devansh54/CourtIQ.git`
- **Repository Visibility:** Private
- **Primary Technologies:** Python 3.12, Sportradar Tennis API v3, SQLite (ANSI SQL), Streamlit, Plotly, Pydantic v2
- **Team Workload Allocation:**
  - Devansh: Overall Architecture, Core Infrastructure & Competitions (50%) [COMPLETED]
  - Venue & Complexes Module Owner: Complexes, Venues & Related Analytics (25%) [YOUR RESPONSIBILITY]
  - Rankings & Analytics Module Owner: Doubles Competitor Rankings & Integration (25%) [SUBSEQUENT OWNER]

---

### 2. CORE ARCHITECTURE & CODEBASE STATUS YOU INHERIT

Begin your task by performing a workspace audit:
1. Read `README.md` and all documentation in `docs/`:
   - `docs/PROJECT_OVERVIEW.md`: Business context and use cases.
   - `docs/REQUIREMENTS.md`: Requirements Traceability Matrix (`REQ-VEN-01` through `REQ-VEN-12`).
   - `docs/ARCHITECTURE.md`: Layered system architecture and sequence diagrams.
   - `docs/DATABASE_DESIGN.md`: Complete 6-table ER diagram and schema specifications.
   - `docs/API_DOCUMENTATION.md`: Sportradar API endpoint mapping and mock fixtures.
   - `docs/DATA_DICTIONARY.md`: Column-level data definitions.
   - `docs/DEVELOPMENT_GUIDELINES.md`: Coding conventions and Git workflow.
   - `docs/TEAM_WORK_ALLOCATION.md`: 50/25/25 distribution and rules.
   - `docs/reference/PROJECT_GUIDE.pdf`: Original 14-page project guide.
2. Run the existing test suite:
   ```bash
   python -m pytest tests -v
   ```
   Verify that all 18 existing tests pass.

---

### 3. SHARED INTERFACES YOU MUST REUSE (DO NOT REWRITE)

Devansh has built and tested reusable infrastructure in `src/courtiq/core/`. You must import and utilize these shared components rather than writing custom HTTP clients or database connections:

1. **Configuration (`src/courtiq/core/config.py`):**
   ```python
   from courtiq.core.config import get_settings
   settings = get_settings()
   ```
2. **Database Engine (`src/courtiq/core/database.py`):**
   ```python
   from courtiq.core.database import get_db
   db = get_db()
   # Use db.fetch_all(sql, params), db.fetch_df(sql, params), db.execute_many(sql, params)
   ```
3. **Sportradar API Client (`src/courtiq/core/api_client.py`):**
   ```python
   from courtiq.core.api_client import SportradarClient
   client = SportradarClient()
   # Automatically handles rate-limits, retries, and offline mock fallback!
   payload = client.get("complexes.json")
   ```
4. **Structured Logging (`src/courtiq/core/logging_config.py`):**
   ```python
   from courtiq.core.logging_config import get_logger
   logger = get_logger("domains.venues")
   ```
5. **Exceptions (`src/courtiq/core/exceptions.py`):**
   Use `DataValidationError`, `TransformationError`, `DatabaseError`.
6. **UI Design System (`src/courtiq/utils/formatting.py`):**
   Use `apply_custom_css()`, `render_metric_card()`, `render_section_header()`.

---

### 4. YOUR EXACT DELIVERABLES (COMPLEXES & VENUES — 25%)

Official API Reference: `https://developer.sportradar.com/tennis/reference/complexes`  
Offline Test Fixture: `tests/fixtures/complexes_sample.json`

#### A. Database Migration: `sql/migrations/002_venues.sql`
Create the two required tables according to the specifications in `docs/DATABASE_DESIGN.md`:
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
   - `complex_id` VARCHAR(50) NOT NULL, FOREIGN KEY REFERENCES complexes(complex_id)
3. Appropriate indexes on `complex_id`, `country_code`, and `city_name`.

#### B. API Extraction: `src/courtiq/domains/venues/extractor.py`
Implement `VenuesExtractor` to call `client.get("complexes.json")` and return the raw JSON dict.

#### C. Data Transformation: `src/courtiq/domains/venues/transformer.py`
Implement `VenuesTransformer`:
- Parse nested `complexes` array from Sportradar API.
- Extract `Complex` entities (`complex_id`, `complex_name`).
- Extract child `Venue` entities (`venue_id`, `venue_name`, `city_name`, `country_name`, `country_code`, `timezone`, `complex_id`).
- Validate data using `src/courtiq/domains/venues/schemas.py`.
- Return `Tuple[List[Complex], List[Venue]]`.

#### D. SQL Repository & Persistence: `src/courtiq/domains/venues/repository.py`
Implement `VenuesRepository`:
- `save_complexes(complexes: List[Complex]) -> int` (idempotent `INSERT OR REPLACE`).
- `save_venues(venues: List[Venue]) -> int` (idempotent `INSERT OR REPLACE`).
- Core count methods: `get_complex_count()`, `get_venue_count()`.
- Repository execution methods for all 7 required SQL queries.

#### E. Mandatory 7 SQL Query Files in `sql/queries/venues/`:
1. `q1_venues_with_complex.sql`: List all venues along with their associated complex name.
2. `q2_venues_count_per_complex.sql`: Count the number of venues in each complex.
3. `q3_venues_by_country.sql`: Get details of venues in a specific country (e.g., Chile).
4. `q4_venues_and_timezones.sql`: Identify all venues and their timezones.
5. `q5_multi_venue_complexes.sql`: Find complexes that have more than one venue.
6. `q6_venues_by_country_group.sql`: List venues grouped by country.
7. `q7_venues_for_specific_complex.sql`: Find all venues for a specific complex (e.g., Nacional).

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
4. The handoff must be a complete, copy-paste-ready instruction prompt for the **Rankings & Analytics Module Owner** describing both Devansh's foundation and your completed venues module, along with step-by-step instructions for the Doubles Competitor Rankings domain and final system regression testing.

---

### 6. GIT BRANCHING & OWNERSHIP RULES

1. Create and work on branch: `feature/venues-complexes`.
2. Do NOT edit `src/courtiq/core/` or `src/courtiq/domains/competitions/`.
3. Never use generic labels such as "Person 1/2/3" or "Developer 1/2/3" in code or documentation.
4. Commit your work with clear messages:
   - `feat(venues): add database migration 002_venues.sql`
   - `feat(venues): implement extractor, transformer and repository`
   - `feat(venues): implement 7 required sql queries and analytics`
   - `feat(venues): build interactive streamlit venues explorer`
   - `test(venues): add unit and integration test suite`
   - `docs(handoff): generate rankings module handoff prompt`
```
