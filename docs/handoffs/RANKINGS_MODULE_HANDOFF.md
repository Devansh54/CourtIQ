# DEVELOPER HANDOFF DIRECTIVE: RANKINGS & ANALYTICS MODULE OWNER

**To:** Nilakshi (Rankings & Analytics Module Owner & Release Lead)  
**From:** Devansh (Lead Software Architect & Competitions Owner) & Mansi (Venue & Complexes Module Owner)  
**Project:** CourtIQ – Tennis Data & Analytics Explorer  
**Workload Allocation:** 25% Total Project Workload (25 Effort Units) — Final Delivery Milestone  
**Parent Milestones:** 
- Milestone 1 (Foundation, PostgreSQL 18 Architecture & Competitions — 50%) Completed & Merged (PR #1, PR #2)
- Milestone 2 (Complexes, Venues & Related Analytics — 25%) Completed & Merged (PR #3, PR #4)  
**Current Project Progress:** **75% Complete**  
**Target Milestone:** Milestone 3 (Doubles Competitor Rankings, Cross-Domain Analytics & Final Product Release — 25%)  
**Effective Date:** 2026-11-14  
**Target Base Branch for Pull Request:** `devansh-foundation-competitions`  

---

> [!IMPORTANT]
> **INSTRUCTIONS FOR THE RECIPIENT:**  
> Copy and paste the entire directive below into your development environment or Antigravity conversation as your master instruction. Begin by inspecting the GitHub repository, verifying local tests, and reading the architectural documentation. All code must target the merged PostgreSQL 18 foundation.

---

```markdown
# COURTIQ — MASTER IMPLEMENTATION DIRECTIVE: DOUBLES RANKINGS & FINAL RELEASE (25%)

## ROLE: RANKINGS & ANALYTICS MODULE OWNER & RELEASE LEAD

You are **Nilakshi**, the **Rankings & Analytics Module Owner & Release Lead** for **CourtIQ – Tennis Data & Analytics Explorer**, working alongside Devansh (Lead Architect & Competitions Owner) and Mansi (Venue & Complexes Module Owner).

The project is currently **75% complete**:
- **Devansh (50%):** Core infrastructure, configuration, rate-limited Sportradar API client with strict LIVE/DEMO dual modes, PostgreSQL 18 database engine with connection pooling (`QueuePool`), least-privilege security roles, Alembic migration framework, exception hierarchies, structured logging, Streamlit design system, and the complete Competitions & Categories domain.
- **Mansi (25%):** Complexes & Venues domain (extraction, transformation, PostgreSQL repository with idempotent upserts, 7 analytical SQL queries, Streamlit venues explorer, and test suite).

Your responsibility is to deliver the final **25% engineering workload**:
1. Implement the complete **Doubles Competitor Rankings** domain.
2. Implement all **6 required analytical SQL queries** (`sql/queries/rankings/`).
3. Build the interactive **Rankings Explorer** in `pages/3_Rankings.py`.
4. Implement the ingestion pipeline in `src/courtiq/ingestion/runner.py` and `scripts/ingest_rankings.py`.
5. Deliver a comprehensive unit and integration test suite in `tests/unit/rankings/` and `tests/integration/test_rankings_pipeline.py`.
6. Conduct final cross-domain regression testing and complete project sign-off.

---

### 1. PROJECT IDENTITY & REPOSITORY OVERVIEW

- **Project Name:** CourtIQ
- **Full Title:** CourtIQ – Tennis Data & Analytics Explorer
- **Tagline:** Explore Competitions. Analyse Rankings. Discover Tennis.
- **GitHub Repository:** `https://github.com/Devansh54/CourtIQ`
- **Git Remote:** `https://github.com/Devansh54/CourtIQ.git`
- **Base Development Branch:** `devansh-foundation-competitions`
- **Feature Branch to Create:** `feature/competitor-rankings`
- **Primary Technologies:** Python 3.12, Sportradar Tennis API v3, PostgreSQL 18 (`postgres:18-alpine`), SQLAlchemy 2.x Core, Psycopg 3 (`psycopg[binary]`), Alembic, Streamlit, Plotly, Pydantic v2
- **Team Workload Allocation:**
  - Devansh: Overall Architecture, PostgreSQL 18 Foundation, Core Infrastructure & Competitions (50%) [COMPLETED]
  - Mansi: Complexes, Venues & Related Analytics (25%) [COMPLETED]
  - Nilakshi: Doubles Competitor Rankings, Integration & Final Release (25%) [YOUR RESPONSIBILITY]

---

### 2. CORE ARCHITECTURE & CODEBASE STATUS YOU INHERIT

Begin your task by performing a workspace audit:
1. Verify that the PostgreSQL 18 container is running healthy:
   ```bash
   docker compose ps
   ```
2. Read the master documentation in `docs/`:
   - `docs/PROJECT_OVERVIEW.md`: Business context and use cases.
   - `docs/REQUIREMENTS.md`: Requirements Traceability Matrix (`REQ-RNK-01` through `REQ-RNK-14`).
   - `docs/ARCHITECTURE.md`: Layered system architecture and sequence diagrams.
   - `docs/DATABASE_DESIGN.md`: Complete 6-table ER diagram and schema specifications.
   - `docs/POSTGRESQL_SETUP.md`: Database credentials, security roles, pooling parameters, and troubleshooting.
   - `docs/API_DOCUMENTATION.md`: Sportradar API endpoint mapping and mock fixtures.
   - `docs/DATA_DICTIONARY.md`: Column-level data definitions.
   - `docs/DEVELOPMENT_GUIDELINES.md`: Coding conventions, Git workflow, and branch rules.
   - `docs/TEAM_WORK_ALLOCATION.md`: 50/25/25 distribution and ownership boundaries.
   - `docs/IMPLEMENTATION_STATUS.md`: Current milestone tracking (75% completed).
3. Run the existing test suite:
   ```bash
   pytest tests -v
   ```
   Verify that all existing tests pass (100% pass rate).

---

### 3. SHARED INTERFACES YOU MUST REUSE

Devansh has built and verified shared infrastructure in `src/courtiq/core/`. You must import and utilize these components:

1. **Configuration (`src/courtiq/core/config.py`):**
   ```python
   from courtiq.core.config import get_settings
   settings = get_settings()
   ```

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
   - `with db.transaction() as conn:` context manager for atomic operations.
   - **Parameter Binding:** Always use named parameter placeholders with `sqlalchemy.text` (e.g. `text("SELECT * FROM competitors WHERE country_code = :country_code")`).

3. **Sportradar API Client (`src/courtiq/core/api_client.py`):**
   ```python
   from courtiq.core.api_client import SportradarClient
   client = SportradarClient()
   payload = client.get("double_competitors_rankings.json")
   ```
   - In `DEMO` mode: returns synthetic fixture `tests/fixtures/rankings_sample.json`.
   - In `LIVE` mode: requires a valid `SPORTRADAR_API_KEY` and enforces a 1 RPS rate limit.

4. **Structured Logging (`src/courtiq/core/logging_config.py`):**
   ```python
   from courtiq.core.logging_config import get_logger
   logger = get_logger("domains.rankings")
   ```

5. **Exceptions (`src/courtiq/core/exceptions.py`):**
   Use `DataValidationError`, `TransformationError`, `DatabaseError`, `APIError`, `ResourceNotFoundError`.

6. **UI Design System (`src/courtiq/utils/formatting.py`):**
   Use `apply_custom_css()`, `render_metric_card()`, `render_section_header()`.

---

### 4. YOUR EXACT DELIVERABLES (RANKINGS & ANALYTICS — 25%)

Official API Endpoint: `https://api.sportradar.com/tennis/trial/v3/en/double_competitors_rankings.json`  
Offline Test Fixture: `tests/fixtures/rankings_sample.json`

#### A. Database Schema Status & Performance Indexes
The baseline tables `competitors` and `competitor_rankings` were established in migrations `0003_rankings.py` and `1c3add79e37f`:
- `competitors`: `competitor_id` VARCHAR(50) PK, `name` VARCHAR(150), `country` VARCHAR(100), `country_code` VARCHAR(10), `abbreviation` VARCHAR(20).
- `competitor_rankings`: `rank_id` SERIAL PK, `rank` INT, `movement` INT, `points` INT, `competitions_played` INT, `competitor_id` VARCHAR(50) FK REFERENCES competitors(competitor_id).

Add performance indexes as specified in `docs/DATABASE_DESIGN.md`:
- `idx_rankings_competitor_id` ON `competitor_rankings(competitor_id)`
- `idx_rankings_rank` ON `competitor_rankings(rank)`
- `idx_competitors_country_code` ON `competitors(country_code)`
via an Alembic migration (e.g. `alembic/versions/0004_rankings_indexes.py` chained from `1c3add79e37f`).

#### B. Pydantic Schemas: `src/courtiq/domains/rankings/schemas.py`
Implement validated Pydantic v2 schemas:
- `Competitor`: `competitor_id`, `name`, `country`, `country_code`, `abbreviation`.
- `CompetitorRanking`: `rank`, `movement`, `points`, `competitions_played`, `competitor_id`.

#### C. API Extractor: `src/courtiq/domains/rankings/extractor.py`
Implement `RankingsExtractor`:
- Calls `client.get("double_competitors_rankings.json")`.
- Validates that the payload contains `rankings` collection.

#### D. Data Transformer: `src/courtiq/domains/rankings/transformer.py`
Implement `RankingsTransformer`:
- Extracts player profiles into `Competitor` models.
- Extracts rank standings into `CompetitorRanking` models.
- Returns `Tuple[List[Competitor], List[CompetitorRanking]]`.

#### E. PostgreSQL Repository: `src/courtiq/domains/rankings/repository.py`
Implement `RankingsRepository`:
- `save_competitors(competitors: List[Competitor]) -> int` using idempotent PostgreSQL upserts:
  ```sql
  INSERT INTO competitors (competitor_id, name, country, country_code, abbreviation)
  VALUES (:competitor_id, :name, :country, :country_code, :abbreviation)
  ON CONFLICT (competitor_id) DO UPDATE SET
      name = EXCLUDED.name,
      country = EXCLUDED.country,
      country_code = EXCLUDED.country_code,
      abbreviation = EXCLUDED.abbreviation;
  ```
- `save_rankings(rankings: List[CompetitorRanking]) -> int` (clearing or upserting weekly ranking snapshot).
- Count methods: `get_competitor_count()`, `get_rankings_count()`.
- Repository execution methods for all 6 required SQL queries returning pandas DataFrames.

#### F. Mandatory 6 SQL Query Files in `sql/queries/rankings/`:
1. `q1_top_ranked_competitors.sql`: List top-ranked doubles competitors sorted by rank ascending.
2. `q2_rankings_by_country.sql`: Filter competitor rankings for a specific country (e.g. `:country_name`).
3. `q3_rank_movement_gainers.sql`: Identify competitors with positive rank movement (`movement > 0`).
4. `q4_competitions_played_vs_points.sql`: Compare competitions played against total ranking points.
5. `q5_unranked_or_zero_movement_competitors.sql`: Identify competitors with no weekly movement (`movement = 0`).
6. `q6_points_distribution_by_country.sql`: Aggregate total ranking points and player count by country.

#### G. Domain Analytics Service: `src/courtiq/domains/rankings/analytics.py`
Implement `RankingsAnalytics` providing:
- Summary KPIs: Total Ranked Competitors, Countries Represented, Average Points, Top Ranked Player, Biggest Rank Gainer.
- Plotly Visualizations:
  - Top 10 doubles competitors by points (horizontal bar chart).
  - Country dominance by total ranking points (pie or donut chart).
  - Competitions played vs. points correlation (scatter plot).

#### H. Ingestion Integration:
Add `ingest_rankings()` to `src/courtiq/ingestion/runner.py` and create `scripts/ingest_rankings.py`.

#### I. Streamlit Rankings Explorer: `pages/3_Rankings.py`
Replace the placeholder with a full-featured dashboard matching `pages/1_Competitions.py` and `pages/2_Venues.py`:
- KPI metric cards across the top.
- Tab 1: Leaderboard & Rankings Distribution (Plotly charts).
- Tab 2: Country Dominance & Points Share.
- Tab 3: Interactive Filter & Search (country, movement filter, player search).
- Tab 4: Required SQL Queries Execution Center (Q1 to Q6 interactive execution).

#### J. Comprehensive Test Suite:
- `tests/unit/rankings/test_schemas.py`
- `tests/unit/rankings/test_extractor.py`
- `tests/unit/rankings/test_transformer.py`
- `tests/unit/rankings/test_repository.py`
- `tests/unit/rankings/test_analytics.py`
- `tests/integration/test_rankings_pipeline.py`
- `tests/integration/test_full_system_regression.py` (verifying all 3 domains simultaneously)

---

### 5. RELEASE & FINAL SIGN-OFF REQUIREMENT

Upon completing, testing, and verifying your 25% implementation:
1. Update `docs/IMPLEMENTATION_STATUS.md` to reflect **100% Total Product Workload Complete**.
2. Update `app.py` telemetry to mark all 3 domains as `ACTIVE / FULLY IMPLEMENTED`.
3. Verify that all test suites pass (100% pass rate in CI).
4. Provide the final project summary report.

---

### 6. GIT BRANCHING & OWNERSHIP RULES

1. Branch off: `devansh-foundation-competitions`.
2. Work on branch: `feature/competitor-rankings`.
3. Open your Pull Request targeting base branch: `devansh-foundation-competitions`.
4. Do NOT modify existing logic in `competitions/` or `venues/`.
5. Never use generic labels such as "Person 1/2/3" or "Developer 1/2/3".
```
