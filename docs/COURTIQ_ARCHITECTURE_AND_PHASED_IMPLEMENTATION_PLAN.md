# COURTIQ — COMPLETE TARGET SOFTWARE ARCHITECTURE & PHASE-WISE IMPLEMENTATION BLUEPRINT

**Product Name:** CourtIQ – Tennis Data & Analytics Explorer  
**Tagline:** Explore Competitions. Analyse Rankings. Discover Tennis.  
**Repository:** [https://github.com/Devansh54/CourtIQ](https://github.com/Devansh54/CourtIQ)  
**Remote Git URL:** `https://github.com/Devansh54/CourtIQ.git`  
**Repository Owner:** `Devansh54` (Private)  
**Document Type:** Master Architecture Blueprint & End-to-End Phased Implementation Plan  
**Document Version:** 2.1.0-REFINED  
**Effective Date:** 2026-11-05  
**Architectural Lead & Core Contributor:** Devansh (50% Project Scope)  
**Specialized Domain Contributors:** Mansi (25% Project Scope) | Nilakshi (25% Project Scope)  
**Status:** ARCHITECTED & RIGOROUSLY AUDITED — PLANNING & REFINEMENT ONLY (AWAITING EXECUTION AUTHORIZATION)  

---

> [!IMPORTANT]
> **GOVERNANCE & EXECUTION DIRECTIVE:**  
> This blueprint represents the single authoritative architectural specification, database strategy, and chronological implementation roadmap for the entire CourtIQ software product. It defines the complete target architecture across all three business domains and establishes a strictly sequential, 10-phase development roadmap.  
> **CURRENT STATUS: PLANNING ONLY.**  
> In accordance with strict project instructions, no code refactoring, schema changes, migrations, branch modifications, or commits are permitted until explicit user authorization is granted.

---

## 1. EXECUTIVE SUMMARY

CourtIQ is an enterprise-grade sports data analytics and visualization platform designed to solve the real-world challenges of collecting, normalizing, querying, and visualizing tennis competition data from the **Sportradar Tennis API (v3)**.

Operating directly on nested sports APIs at runtime introduces critical failure modes: excessive latency, rapid exhaustion of strict trial rate limits (1 request per second, 1,000 monthly calls), and an inability to run complex analytical aggregations. CourtIQ solves these challenges through a **Modular Domain-Driven Layered Architecture**:
1. **Explicit Dual-Mode API Integration:** Strictly separated **`LIVE`** and **`DEMO`** operating modes, guaranteeing fail-fast authentication validation in production and safe, zero-cost synthetic demonstrations without silent data contamination.
2. **Strict Schema Normalization:** Pydantic v2 data validation transforming hierarchical JSON objects into normalized relational tuples.
3. **Robust Relational Persistence:** A normalized six-table relational schema enforcing referential integrity, primary/foreign keys, indexed lookups, and idempotent persistence.
4. **Optimized SQL Analytics:** 20 pre-compiled, parameterized analytical SQL queries delivering high-performance aggregations across competition structures, venue geographies, and player rankings.
5. **Interactive Sports Intelligence UI:** A multi-page Streamlit web application featuring a global KPI command center, cross-filtering charts, interactive hierarchy trees, and player leaderboards.

The engineering workload is distributed across three contributors following an uncompromising sequential relay model:
- **Devansh (50%):** Overall System Architecture, Core Shared Infrastructure, Relational Database Foundation, and Complete Competitions & Categories Domain (Phases 1 to 5).
- **Mansi (25%):** Complexes & Venues Data Engineering, Relational Storage, Analytical Queries, Streamlit Venues Explorer, and Handoff Generation (Phases 6, 7, and 8A).
- **Nilakshi (25%):** Doubles Competitor Rankings Data Engineering, Historical Snapshot Management, Analytical Leaderboards, Streamlit Rankings Explorer, and Accountable Lead for Final System Integration & Release (Phases 8B, 9, and 10).

---

## 2. SOURCE DOCUMENT ANALYSIS & REQUIREMENTS TRACEABILITY

The primary source of truth for CourtIQ is the 14-page project guide: `Game Analytics: Unlocking Tennis Data with SportRadar API (1)-2.pdf`. A comprehensive audit of all 14 pages yields the following technical requirements and scope boundaries.

### 2.1 Problem Statement & Business Use Cases
- **Problem Statement (PDF Page 1):** Develop a comprehensive solution for managing, visualizing, and analyzing sports competition data extracted from the Sportradar API by parsing JSON data, storing structured information in a relational database, and providing intuitive insights into tournaments, competition hierarchies, and event details.
- **Use Case 1 — Event Exploration (PDF Page 1):** Enable analysts to navigate through competition hierarchies (e.g., ATP Vienna events, Grand Slams, qualifying vs. main draw draws).
- **Use Case 2 — Trend Analysis (PDF Page 1):** Visualize the distribution of events by format (singles, doubles), participant gender (men, women, mixed), and competition category (ATP, WTA, ITF).
- **Use Case 3 — Performance Insights (PDF Page 1):** Analyze doubles player performance, weekly ranking volatility (movements), and tournament activity levels.
- **Use Case 4 — Decision Support (PDF Page 1):** Provide data-driven insights to event organizers and sports governing bodies regarding venue capacities, geographic distribution, and timezone scheduling.

### 2.2 Core Technical Endpoints & Relational Specifications
The project guide mandates data collection from three specific Sportradar endpoints:

1. **Competitions Endpoint (PDF Pages 2–4):**  
   `https://developer.sportradar.com/tennis/reference/competitions`  
   - Table `categories`: `category_id` (VARCHAR(50), PK), `category_name` (VARCHAR(100), NOT NULL).  
   - Table `competitions`: `competition_id` (VARCHAR(50), PK), `competition_name` (VARCHAR(100), NOT NULL), `parent_id` (VARCHAR(50), NULLABLE), `type` (VARCHAR(20), NOT NULL), `gender` (VARCHAR(10), NOT NULL), `category_id` (VARCHAR(50), FK -> categories).  
   - *7 Mandated SQL Queries (Q1 to Q7).*

2. **Complexes Endpoint (PDF Pages 4–5):**  
   `https://developer.sportradar.com/tennis/reference/complexes`  
   - Table `complexes`: `complex_id` (VARCHAR(50), PK), `complex_name` (VARCHAR(100), NOT NULL).  
   - Table `venues`: `venue_id` (VARCHAR(50), PK), `venue_name` (VARCHAR(100), NOT NULL), `city_name` (VARCHAR(100), NOT NULL), `country_name` (VARCHAR(100), NOT NULL), `country_code` (CHAR(3), NOT NULL), `timezone` (VARCHAR(100), NOT NULL), `complex_id` (VARCHAR(50), FK -> complexes).  
   - *7 Mandated SQL Queries (Q8 to Q14).*

3. **Doubles Competitor Rankings Endpoint (PDF Pages 6–8):**  
   `https://developer.sportradar.com/tennis/reference/doubles-competitor-rankings`  
   - Table `competitors`: `competitor_id` (VARCHAR(50), PK), `name` (VARCHAR(100), NOT NULL), `country` (VARCHAR(100), NOT NULL), `country_code` (CHAR(3), NOT NULL), `abbreviation` (VARCHAR(10), NOT NULL).  
   - Table `competitor_rankings`: `rank_id` (INT, PK AUTO_INCREMENT), `rank` (INT, NOT NULL), `movement` (INT, NOT NULL), `points` (INT, NOT NULL), `competitions_played` (INT, NOT NULL), `competitor_id` (VARCHAR(50), FK -> competitors).  
   - *6 Mandated SQL Queries (Q15 to Q20).*

### 2.3 Requirements Traceability Matrix (RTM)

| Domain | Requirement ID | PDF Ref | Exact Description | Target Module | Owner |
|---|---|---|---|---|---|
| **INFRA** | `REQ-INFRA-01` | Page 2, 10 | Centralized environment configuration supporting explicit LIVE/DEMO modes | `src/courtiq/core/config.py` | Devansh |
| **INFRA** | `REQ-INFRA-02` | Page 2, 11 | Relational database manager with ACID transactions & foreign keys | `src/courtiq/core/database.py` | Devansh |
| **INFRA** | `REQ-INFRA-03` | Page 2, 10 | Sportradar HTTP client with rate-limiting (1 RPS) & fail-fast auth | `src/courtiq/core/api_client.py` | Devansh |
| **INFRA** | `REQ-INFRA-04` | Page 10, 11 | Structured logging & domain exception hierarchy | `src/courtiq/core/logging_config.py` | Devansh |
| **INFRA** | `REQ-INFRA-05` | Page 2, 10 | Database migration engine tracking `schema_migrations` | `src/courtiq/core/database.py` | Devansh |
| **INFRA** | `REQ-INFRA-06` | Page 8, 11 | Master Streamlit shell, custom CSS, mode badges & navigation | `app.py`, `src/courtiq/utils/formatting.py` | Devansh |
| **COMP** | `REQ-COMP-01` | Page 2 | Fetch competitions from `/competitions.json` | `src/courtiq/domains/competitions/extractor.py` | Devansh |
| **COMP** | `REQ-COMP-02` | Page 2 | Normalize nested JSON into `categories` and `competitions` | `src/courtiq/domains/competitions/transformer.py` | Devansh |
| **COMP** | `REQ-COMP-03` | Page 2-3 | Table DDL for `categories` & `competitions` with FKs & indexes | `sql/migrations/001_competitions.sql` | Devansh |
| **COMP** | `REQ-COMP-04` | Page 3 | SQL Q1: List all competitions along with category name | `sql/queries/competitions/q1_list_with_category.sql` | Devansh |
| **COMP** | `REQ-COMP-05` | Page 3 | SQL Q2: Count the number of competitions in each category | `sql/queries/competitions/q2_count_by_category.sql` | Devansh |
| **COMP** | `REQ-COMP-06` | Page 4 | SQL Q3: Find all competitions of type 'doubles' | `sql/queries/competitions/q3_doubles_competitions.sql` | Devansh |
| **COMP** | `REQ-COMP-07` | Page 4 | SQL Q4: Competitions belonging to specific category (ITF Men) | `sql/queries/competitions/q4_by_specific_category.sql` | Devansh |
| **COMP** | `REQ-COMP-08` | Page 4 | SQL Q5: Identify parent competitions and sub-competitions | `sql/queries/competitions/q5_parent_sub_hierarchy.sql` | Devansh |
| **COMP** | `REQ-COMP-09` | Page 4 | SQL Q6: Distribution of competition types by category | `sql/queries/competitions/q6_type_distribution_by_category.sql` | Devansh |
| **COMP** | `REQ-COMP-10` | Page 4 | SQL Q7: List competitions with no parent (top-level) | `sql/queries/competitions/q7_top_level_competitions.sql` | Devansh |
| **COMP** | `REQ-COMP-11` | Page 8-10 | Interactive Streamlit Competitions Explorer & hierarchy tree | `pages/1_Competitions.py` | Devansh |
| **VEN** | `REQ-VEN-01` | Page 4 | Fetch complexes payload from `/complexes.json` | `src/courtiq/domains/venues/extractor.py` | Mansi |
| **VEN** | `REQ-VEN-02` | Page 4-5 | Normalize nested JSON into `complexes` and `venues` | `src/courtiq/domains/venues/transformer.py` | Mansi |
| **VEN** | `REQ-VEN-03` | Page 4-5 | Table DDL for `complexes` and `venues` with FKs & indexes | `sql/migrations/002_venues.sql` | Mansi |
| **VEN** | `REQ-VEN-04` | Page 5 | SQL Q8: List venues along with associated complex name | `sql/queries/venues/q1_venues_with_complex.sql` | Mansi |
| **VEN** | `REQ-VEN-05` | Page 5 | SQL Q9: Count the number of venues in each complex | `sql/queries/venues/q2_venues_count_per_complex.sql` | Mansi |
| **VEN** | `REQ-VEN-06` | Page 5 | SQL Q10: Details of venues in a specific country (Chile) | `sql/queries/venues/q3_venues_by_country.sql` | Mansi |
| **VEN** | `REQ-VEN-07` | Page 5 | SQL Q11: Identify all venues and their timezones | `sql/queries/venues/q4_venues_and_timezones.sql` | Mansi |
| **VEN** | `REQ-VEN-08` | Page 5 | SQL Q12: Find complexes that have more than one venue | `sql/queries/venues/q5_multi_venue_complexes.sql` | Mansi |
| **VEN** | `REQ-VEN-09` | Page 5 | SQL Q13: List venues grouped by country | `sql/queries/venues/q6_venues_by_country_group.sql` | Mansi |
| **VEN** | `REQ-VEN-10` | Page 5 | SQL Q14: Find all venues for a specific complex (Nacional) | `sql/queries/venues/q7_venues_for_specific_complex.sql` | Mansi |
| **VEN** | `REQ-VEN-11` | Page 8-10 | Interactive Streamlit Venues Explorer & geographic charts | `pages/2_Venues.py` | Mansi |
| **RNK** | `REQ-RNK-01` | Page 6 | Fetch rankings from `/double_competitor_rankings.json` | `src/courtiq/domains/rankings/extractor.py` | Nilakshi |
| **RNK** | `REQ-RNK-02` | Page 6-7 | Normalize JSON into `competitors` and `competitor_rankings` | `src/courtiq/domains/rankings/transformer.py` | Nilakshi |
| **RNK** | `REQ-RNK-03` | Page 6-7 | Table DDL for `competitors` and `competitor_rankings` | `sql/migrations/003_rankings.sql` | Nilakshi |
| **RNK** | `REQ-RNK-04` | Page 7 | SQL Q15: Get all competitors with their rank and points | `sql/queries/rankings/q1_competitors_rank_points.sql` | Nilakshi |
| **RNK** | `REQ-RNK-05` | Page 7 | SQL Q16: Find competitors ranked in the top 5 | `sql/queries/rankings/q2_top_5_competitors.sql` | Nilakshi |
| **RNK** | `REQ-RNK-06` | Page 8 | SQL Q17: List competitors with no rank movement (stable) | `sql/queries/rankings/q3_stable_rank_competitors.sql` | Nilakshi |
| **RNK** | `REQ-RNK-07` | Page 8 | SQL Q18: Total points of competitors from country (Croatia) | `sql/queries/rankings/q4_points_by_country.sql` | Nilakshi |
| **RNK** | `REQ-RNK-08` | Page 8 | SQL Q19: Count the number of competitors per country | `sql/queries/rankings/q5_competitors_per_country.sql` | Nilakshi |
| **RNK** | `REQ-RNK-09` | Page 8 | SQL Q20: Competitors with highest points in current week | `sql/queries/rankings/q6_highest_points_competitors.sql` | Nilakshi |
| **RNK** | `REQ-RNK-10` | Page 8-10 | Interactive Streamlit Rankings Explorer, Leaderboard & Search | `pages/3_Rankings.py` | Nilakshi |
| **INT** | `REQ-INT-01` | Page 8, 10 | Unified Multi-domain Ingestion Orchestrator (`ingest_all`) | `src/courtiq/ingestion/runner.py` | Nilakshi (Lead) / All |
| **INT** | `REQ-INT-02` | Page 9-11 | System-wide cross-domain regression test suite | `tests/integration/test_full_system.py` | Nilakshi (Lead) / All |

---

## 3. EXISTING REPOSITORY & GIT SAFETY AUDIT

### 3.1 Forensic Audit of Git History & Tree Restoration
In the previous activity cycle, an audit was conducted on the working tree following commit `ce61e62`:
1. **Commit `ce61e62` Integrity:** Commit `ce61e62549f7a6a26e4845fc4de868369e8cbae9` ("feat(core): initialize CourtIQ foundation and complete competitions module") contains all 72 initial files (5,265 lines of code and documentation). This commit is pushed to and verified on GitHub remote `origin/devansh-foundation-competitions` and `origin/main`.
2. **Analysis of `git restore .`:** The command `git restore .` was executed when 68 files appeared as "modified" in `git status`. Forensic inspection of `git diff` revealed that these modifications were strictly Windows CRLF vs. Linux LF line-ending translations (`warning: in the working copy of ..., LF will be replaced by CRLF the next time Git touches it`). Restoring the tree did **NOT** discard any code or documentation changes; it simply normalized the local filesystem working copy to the exact bytes recorded in Git commit `ce61e62`.
3. **Untracked File Resolution:** The previous summary report stated "working tree clean" based on an intermediate check before creating `docs/COURTIQ_ARCHITECTURE_AND_PHASED_IMPLEMENTATION_PLAN.md`. Once written, that markdown file became an untracked file. In accordance with the user's strict planning-only directive, this planning document remains intentionally untracked on disk without staging, committing, or pushing.
4. **Current Test Suite Validation:** Running `pytest tests -v` confirms that **18 of 18 tests pass in 1.59s**. The codebase is intact, stable, and completely uncorrupted.

---

## 4. RELATIONAL DATABASE ARCHITECTURE & RE-EVALUATION

### 4.1 Evaluation of Database Engines: PDF Mandate vs. Current State
Page 10 of the original project guide specifies under Technical Tags:
> **Database : MySQL/PostgreSQL**

Furthermore, the schema specifications on Pages 4 and 6 use MySQL-specific conventions:
- `rank_id INT PRIMARY KEY AUTO_INCREMENT` (MySQL syntax).

The initial implementation in `src/courtiq/core/database.py` implemented a zero-dependency **SQLite** manager (`data/courtiq.db`) utilizing Python's standard `sqlite3` library. While SQLite provided instant verification during initial development, **it cannot be presented as a 100% compliant final submission engine** without formally addressing the PDF's explicit MySQL/PostgreSQL requirement.

### 4.2 Comprehensive Database Compatibility & Limitation Analysis
It is technically inaccurate to claim that standard ANSI SQL is universally portable across SQLite, MySQL, and PostgreSQL. Crucial dialect incompatibilities exist across the four major relational operations:

| Dialect Feature | SQLite 3 (Current Local) | MySQL 8.0+ (PDF Mandated) | PostgreSQL 16+ (PDF Mandated) | Impact on CourtIQ |
|---|---|---|---|---|
| **Auto-Increment PK** | `INTEGER PRIMARY KEY AUTOINCREMENT` | `INT PRIMARY KEY AUTO_INCREMENT` | `SERIAL PRIMARY KEY` or `INT GENERATED ALWAYS AS IDENTITY` | Migration script DDL for `competitor_rankings` must be dialect-specific. |
| **Upsert Syntax** | `INSERT OR REPLACE INTO ...` or `ON CONFLICT (...) DO UPDATE` | `INSERT INTO ... ON DUPLICATE KEY UPDATE col=VALUES(col)` | `INSERT INTO ... ON CONFLICT (id) DO UPDATE SET col = EXCLUDED.col` | Repository `save_*` methods cannot use identical upsert statements across engines. |
| **Param Placeholders** | `?` (qmark style) | `%s` (format style via `pymysql` / `mysql-connector`) | `%s` or `$1, $2` (via `psycopg2` / `asyncpg`) | Query parameter binding in `DatabaseManager` must adapt to the driver's `paramstyle`. |
| **Foreign Key Enforce**| Disabled by default; requires `PRAGMA foreign_keys = ON;` per connection | Enforced by default on InnoDB engines | Enforced by default | SQLite requires explicit per-connection initialization. |
| **Concurrency / Lock** | Database-level write lock; concurrent Streamlit writes cause `sqlite3.OperationalError: database is locked` | Row-level locking (MVCC); high concurrent read/write throughput | Row-level locking (MVCC); enterprise concurrency | SQLite degrades under simultaneous multi-user dashboard filtering if writes occur. |

### 4.3 Architectural Database Recommendation
To achieve enterprise engineering rigor while preserving frictionless evaluatability, CourtIQ adopts the following two-tier database strategy:

```mermaid
flowchart TD
    subgraph Primary_Target["1. Primary Development & Final Submission Database (Recommended)"]
        MYSQL["MySQL 8.0+ (or PostgreSQL 16+)"]
        REASON1["100% Complies with PDF Page 10 ('Database: MySQL/PostgreSQL')"]
        REASON2["Native AUTO_INCREMENT and row-level concurrency for Streamlit"]
    end

    subgraph Testing_Target["2. Local Offline Testing Database (Lightweight Fallback)"]
        SQLITE["SQLite 3 (data/courtiq.db)"]
        REASON3["Zero-dependency test runs (Pytest tmp_path) and standalone review"]
        REASON4["Embedded directly in Python standard library"]
    end

    Primary_Target -.->|Dialect Adapter Layer| DB_MGR["src/courtiq/core/database.py"]
    Testing_Target -.->|Dialect Adapter Layer| DB_MGR
```

1. **Primary Submission Database (Recommended): MySQL 8.0+** (or PostgreSQL 16+).  
   - Directly satisfies the PDF specification ("MySQL/PostgreSQL", `AUTO_INCREMENT`).
   - Configured via `DATABASE_URL=mysql+pymysql://user:password@localhost:3306/courtiq` in `.env`.
   - Migration files: `sql/migrations/mysql/` (or PostgreSQL equivalent).
2. **Local Testing Database: SQLite 3 (`data/courtiq.db`).**  
   - Retained exclusively for automated unit tests in `tests/conftest.py` using `tmp_path` fixtures, enabling fast, isolated test execution on machines without a running MySQL server.
3. **Migration & Driver Strategy:**  
   - In Phase 6, `DatabaseManager` will be enhanced with a lightweight dialect detector that translates parameter markers (`?` vs `%s`) and applies dialect-appropriate DDL scripts.

> [!CAUTION]
> **DECISION REQUIRING APPROVAL:**  
> The final selection of the primary submission database (MySQL 8.0+ vs. PostgreSQL 16+ vs. retaining SQLite with an explicit deviation waiver) is **PENDING DEVANSH'S ARCHITECTURAL SIGN-OFF**.

---

## 5. EXPLICIT DUAL-MODE API & SYNTHETIC DATA ARCHITECTURE

### 5.1 Elimination of Automatic Fallback
The initial implementation of `SportradarClient` automatically fell back to mock JSON fixtures whenever an API call failed or credentials were empty. While convenient during initial bootstrapping, this behavior is hazardous in production because it causes **silent data contamination**—an invalid API key or network disruption would masquerade as a successful API call with synthetic data.

CourtIQ replaces this behavior with an **Explicit Dual-Mode Operating Model**:

```mermaid
stateDiagram-v2
    [*] --> CheckMode

    state CheckMode {
        COURTIQ_MODE --> LIVE_MODE : COURTIQ_MODE=LIVE
        COURTIQ_MODE --> DEMO_MODE : COURTIQ_MODE=DEMO
        COURTIQ_MODE --> ConfigError : Undefined / Invalid Mode
    }

    state LIVE_MODE {
        ValidateKey --> HTTPRequest : Key Valid
        ValidateKey --> AuthenticationError : Key Missing or Invalid (401/403)
        HTTPRequest --> RateLimiter : 1.0 RPS Pacing
        RateLimiter --> RemoteAPI : Dispatch HTTPS
        RemoteAPI --> Success : 200 OK
        RemoteAPI --> RateLimitError : 429 Too Many Requests (Retries Exhausted)
        RemoteAPI --> APIError : 5xx / Network Failure
    }

    state DEMO_MODE {
        LoadFixture --> VerifiedSyntheticJSON : tests/fixtures/*.json
        VerifiedSyntheticJSON --> BannerFlag : Set st.warning('DEMO MODE')
        BannerFlag --> UIOutput
    }

    AuthenticationError --> [*] : Fail Fast with Explicit Error
    RateLimitError --> [*] : Fail Fast with Explicit Error
    Success --> [*] : Persist Real Data
    UIOutput --> [*] : Render Demo Data with Clear Visual Banner
```

### 5.2 Operating Mode Specifications

#### Mode 1: `COURTIQ_MODE=LIVE`
- **Execution Target:** Real Sportradar Tennis API v3 (`https://api.sportradar.com/tennis/trial/v3/en`).
- **Authentication:** Requires valid `SPORTRADAR_API_KEY` in `.env`.
- **Failure Behavior:** If credentials are missing, empty, or rejected with HTTP 401/403, the client **FAILS FAST** and raises a descriptive `AuthenticationError`. It **NEVER** switches to mock fixtures.
- **Rate-Limiting:** Paced at 1.0 request per second to protect trial limits.
- **UI Telemetry:** The Streamlit header displays a green `LIVE DATA (Sportradar API v3)` badge.

#### Mode 2: `COURTIQ_MODE=DEMO`
- **Execution Target:** Synthetic test fixtures stored in `tests/fixtures/`.
- **Zero Network Cost:** Does not make external network requests and does not consume monthly trial API quotas.
- **Visual Transparency:** The Streamlit interface displays an unmistakable orange warning banner:  
  `⚠️ DEMO MODE ACTIVE: Rendering synthetic demonstration data from tests/fixtures/. No live API calls are being made.`
- **Telemetry & Logs:** All log messages explicitly record: `[DEMO MODE] Loading synthetic fixture: competitions_sample.json`.

---

## 6. DOUBLES RANKINGS SNAPSHOT ARCHITECTURE & API SCHEMA ANALYSIS

### 6.1 Official Sportradar Doubles Rankings API Analysis
Official Sportradar Tennis API v3 endpoint:  
`https://api.sportradar.com/tennis/trial/v3/en/double_competitor_rankings.json`

An inspection of Sportradar API payload patterns reveals that ranking responses are delivered as follows:
```json
{
  "generated_at": "2024-11-04T12:00:00Z",
  "rankings": [
    {
      "name": "ATP Doubles",
      "year": 2024,
      "week": 44,
      "competitor_rankings": [
        {
          "rank": 1,
          "movement": 0,
          "points": 7820,
          "competitions_played": 22,
          "competitor": {
            "id": "sr:competitor:101",
            "name": "Granollers, Marcel",
            "country": "Spain",
            "country_code": "ESP",
            "abbreviation": "GRA"
          }
        }
      ]
    }
  ]
}
```

> [!WARNING]
> **CRITICAL ARCHITECTURAL FINDING:**  
> While the outer payload includes `"generated_at": "..."` and some responses include `"year"` and `"week"`, the **project guide (PDF Pages 6–7) explicitly mandates a strict 6-column relational schema** for `competitor_rankings` that **omits** all weekly identifiers.

### 6.2 Comparison of Schema Options

```mermaid
classDiagram
    class PDF_Baseline_Schema {
        +int rank_id PK AUTO_INCREMENT
        +int rank
        +int movement
        +int points
        +int competitions_played
        +varchar(50) competitor_id FK
    }

    class Extended_Snapshot_Schema {
        +int rank_id PK AUTO_INCREMENT
        +int rank
        +int movement
        +int points
        +int competitions_played
        +varchar(50) competitor_id FK
        +date snapshot_date
        +int snapshot_year
        +int snapshot_week
    }

    PDF_Baseline_Schema <|-- Extended_Snapshot_Schema : Evaluated in Phase 8B
```

#### Option A: Baseline 6-Column Guide Schema (Strict Compliance)
- **Columns:** `rank_id`, `rank`, `movement`, `points`, `competitions_played`, `competitor_id`.
- **Semantics:** Represents the *current* ranking standings. Repetitive ingestion replaces or updates existing records (`INSERT OR REPLACE` / `ON DUPLICATE KEY UPDATE` keyed on `competitor_id`).
- **Pros:** 100% compliant with the evaluation rubric; zero discrepancy with PDF Pages 6–7.
- **Cons:** Historical week-over-week trends cannot be queried across time.

#### Option B: Extended Snapshot Schema (Enterprise Historical Tracking)
- **Columns:** Baseline 6 columns + `snapshot_date DATE NOT NULL`, `snapshot_year INT`, `snapshot_week INT`.
- **Semantics:** Each weekly ingestion creates an immutable snapshot.
- **Pros:** Enables multi-week trend graphs and rank volatility tracking across time.
- **Cons:** Requires adding non-PDF columns; requires composite uniqueness on `(competitor_id, snapshot_date)`.

### 6.3 Conditions for Adopting the Extension
The extended schema shall be adopted **ONLY IF ALL THREE CONDITIONS ARE MET** during Phase 8B:
1. Live endpoint inspection confirms that `generated_at` or `year`/`week` are reliably present in all live responses without nullability.
2. The stakeholder/evaluator confirms that historical multi-week tracking is desired over single-snapshot storage.
3. **Formal approval is granted by Devansh in Phase 8B.** Otherwise, Option A (Baseline Schema) remains the enforced standard.

---

## 7. TASK-LEVEL WORKLOAD ESTIMATION & MATHEMATICAL PROOF

### 7.1 Engineering Effort Taxonomy
Workload is calculated across six standard software engineering activity categories:
- **DEV:** Software architecture, DDL migrations, Python coding, and ETL engineering.
- **TST:** Unit testing, mock fixture authoring, pipeline integration testing, and SQL verification.
- **DBG:** Bugfixing, edge-case handling, data sanitization, and transaction tuning.
- **DOC:** Requirements tracking, schema documentation, data dictionaries, and architectural updates.
- **INT:** Cross-domain module integration, shared interface consumption, and Streamlit dashboard wiring.
- **HND:** Developer handoff prompt generation, PR reviews, and code handovers.

### 7.2 Detailed Task-Level Workload Breakdown (100 Total Units)

```mermaid
gantt
    title CourtIQ 100-Unit Engineering Workload Allocation
    dateFormat X
    axisFormat %d%%
    section Devansh (50%)
    P1: Architecture & RTM (10 Units)        :active, p1, 0, 10
    P2: Core Infra & DB Engine (10 Units)    :active, p2, 10, 20
    P3: Competitions ETL (10 Units)          :active, p3, 20, 30
    P4: Competitions SQL & UI (10 Units)     :active, p4, 30, 40
    P5: Validation & Handoff 1 (10 Units)    :active, p5, 40, 50
    section Mansi (25%)
    P6: Venues ETL & DDL (10 Units)          :        p6, 50, 60
    P7: Venues SQL & UI (10 Units)           :        p7, 60, 70
    P8A: Venues Verify & Handoff 2 (5 Units) :        p8a, 70, 75
    section Nilakshi (25%)
    P8B: Rankings Onboarding (5 Units)       :        p8b, 75, 80
    P9: Rankings ETL, SQL & UI (10 Units)    :        p9, 80, 90
    P10: Full Integration & Release (10 Units):       p10, 90, 100
```

| Phase ID & Description | Owner | Activity Breakdown (DEV / TST / DBG / DOC / INT / HND) | Total Units | Share of Project |
|---|:---:|---|:---:|:---:|
| **Phase 1:** Requirements Analysis & Target Architecture | **Devansh** | DEV: 4 \| DOC: 5 \| TST: 1 | **10 Units** | **10.0%** |
| **Phase 2:** Core Infrastructure & Database Foundation | **Devansh** | DEV: 5 \| TST: 3 \| DBG: 1 \| DOC: 1 | **10 Units** | **10.0%** |
| **Phase 3:** Competitions Data Pipeline & Storage | **Devansh** | DEV: 5 \| TST: 3 \| DBG: 1 \| DOC: 1 | **10 Units** | **10.0%** |
| **Phase 4:** Competitions Analytics & Streamlit UI | **Devansh** | DEV: 5 \| TST: 2 \| DBG: 1 \| DOC: 1 \| INT: 1 | **10 Units** | **10.0%** |
| **Phase 5:** Core Validation, Contracts & Handoff 1 | **Devansh** | TST: 3 \| DBG: 2 \| DOC: 2 \| HND: 3 | **10 Units** | **10.0%** |
| **DEVANSH SUBTOTAL** | **Devansh** | **DEV: 19 \| TST: 12 \| DBG: 5 \| DOC: 10 \| INT: 1 \| HND: 3** | **50 Units** | **50.0%** |
| **Phase 6:** Complexes & Venues Data Engineering | **Mansi** | DEV: 5 \| TST: 3 \| DBG: 1 \| DOC: 1 | **10 Units** | **10.0%** |
| **Phase 7:** Venues Analytics & Streamlit UI | **Mansi** | DEV: 5 \| TST: 2 \| DBG: 1 \| DOC: 1 \| INT: 1 | **10 Units** | **10.0%** |
| **Phase 8A:** Venues Completion, Check & Handoff 2 | **Mansi** | TST: 1 \| DBG: 1 \| DOC: 1 \| HND: 2 | **5 Units** | **5.0%** |
| **MANSI SUBTOTAL** | **Mansi** | **DEV: 10 \| TST: 6 \| DBG: 3 \| DOC: 3 \| INT: 1 \| HND: 2** | **25 Units** | **25.0%** |
| **Phase 8B:** Rankings Onboarding & Design Validation | **Nilakshi**| DEV: 2 \| TST: 1 \| DOC: 1 \| INT: 1 | **5 Units** | **5.0%** |
| **Phase 9:** Doubles Rankings & Competitor Analytics | **Nilakshi**| DEV: 5 \| TST: 2 \| DBG: 1 \| DOC: 1 \| INT: 1 | **10 Units** | **10.0%** |
| **Phase 10:** Final System Integration & Release Lead | **Nilakshi**| DEV: 2 \| TST: 4 \| DBG: 2 \| DOC: 1 \| INT: 1 | **10 Units** | **10.0%** |
| **NILAKSHI SUBTOTAL** | **Nilakshi**| **DEV: 9 \| TST: 7 \| DBG: 3 \| DOC: 3 \| INT: 3** | **25 Units** | **25.0%** |
| **TOTAL PRODUCT WORKLOAD** | **Team** | **DEV: 38 \| TST: 25 \| DBG: 11 \| DOC: 16 \| INT: 5 \| HND: 5** | **100 Units** | **100.0%** |

$$\text{Devansh Total} = 10 + 10 + 10 + 10 + 10 = \mathbf{50 \text{ Units (50.0\%)}}$$
$$\text{Mansi Total} = 10 + 10 + 5 = \mathbf{25 \text{ Units (25.0\%)}}$$
$$\text{Nilakshi Total} = 5 + 10 + 10 = \mathbf{25 \text{ Units (25.0\%)}}$$

---

## 8. PHASE 10 OWNERSHIP & DEFECT GOVERNANCE ARCHITECTURE

### 8.1 Accountable Release Leadership
**Nilakshi is the Accountable Lead for Phase 10 (Final System Integration, Regression & Release Verification).**

As the release lead, Nilakshi:
1. Orchestrates the master ingestion workflow (`ingest_all` in `src/courtiq/ingestion/runner.py`).
2. Implements the cross-domain global KPI telemetry on the homepage (`app.py`).
3. Authors and executes the master end-to-end regression test suite (`tests/integration/test_full_system.py`) that asserts all 20 SQL queries simultaneously.
4. Manages the final integration branch, release tagging (`v1.0.0`), and capstone delivery.

### 8.2 Defect Governance & Escalation Matrix
To ensure that defect resolution work is counted fairly within the 50–25–25 allocation without shifting burdens across contributors, defects discovered during Phase 10 regression testing are routed according to strict domain ownership:

```mermaid
flowchart TD
    FAIL["Phase 10 Regression Test Failure Detected"] --> TRIAGE{"Triage Failure Domain"}

    TRIAGE -->|Core Config, DB Engine, Competitions, Q1-Q7| DEV_FIX["Devansh Fixes Defect (Budgeted in Devansh Phase 5 Contingency)"]
    TRIAGE -->|Complexes, Venues, Q8-Q14, Venues UI| MANSI_FIX["Mansi Fixes Defect (Budgeted in Mansi Phase 8A Contingency)"]
    TRIAGE -->|Rankings, Q15-Q20, Global KPI, Cross-Wiring| NILAKSHI_FIX["Nilakshi Fixes Defect (Budgeted in Nilakshi Phase 10 Allocation)"]

    DEV_FIX --> RE_TEST["Nilakshi Re-runs Full Regression Suite"]
    MANSI_FIX --> RE_TEST
    NILAKSHI_FIX --> RE_TEST
    RE_TEST -->|100% Pass| RELEASE["Approve v1.0.0 Release"]
```

| Domain / Component | Defect Owner | Effort Accounting | Escalation Rule |
|---|:---:|---|---|
| **Shared Core Infrastructure** (`src/courtiq/core/`) | **Devansh** | Accounted within Devansh's Phase 5 bugfix contingency (2 units). | Mansi/Nilakshi log bug report; Devansh patches core. |
| **Competitions Domain & SQL Q1–Q7** | **Devansh** | Accounted within Devansh's Phase 4/5 bugfix contingency (2 units). | Devansh resolves data or query discrepancies. |
| **Venues Domain & SQL Q8–Q14** | **Mansi** | Accounted within Mansi's Phase 8A bugfix contingency (1 unit). | Mansi resolves venue normalization or query bugs. |
| **Rankings Domain & SQL Q15–Q20** | **Nilakshi** | Accounted within Nilakshi's Phase 9/10 bugfix allocation (2 units). | Nilakshi resolves ranking calculation or leaderboard bugs. |
| **Cross-Domain Integration & Global UI** | **Nilakshi** | Accounted within Nilakshi's Phase 10 integration allocation (2 units).| Nilakshi resolves navigation or orchestration defects. |

---

## 9. SEQUENTIAL LIFECYCLE, DEPENDENCY GRAPH & PHASE GATES

```mermaid
flowchart TD
    subgraph Milestone1["Milestone 1: Foundation & Competitions (Devansh — 50 Units)"]
        P1["Phase 1: Architecture & RTM (10u)"] --> P2["Phase 2: Core Infra & DB Engine (10u)"]
        P2 --> P3["Phase 3: Competitions ETL Pipeline (10u)"]
        P3 --> P4["Phase 4: Competitions SQL & UI (10u)"]
        P4 --> P5["Phase 5: Core Testing & Handoff 1 (10u)"]
        G1{"Gate 1: 18/18 Tests Pass, Remote Synced"}
        P5 --> G1
    end

    subgraph Milestone2["Milestone 2: Complexes & Venues (Mansi — 25 Units)"]
        H1["docs/handoffs/VENUES_MODULE_HANDOFF.md"]
        G1 --> H1
        H1 --> P6["Phase 6: Venues ETL & 002 Migration (10u)"]
        P6 --> P7["Phase 7: Venues SQL & UI (10u)"]
        P7 --> P8A["Phase 8A: Venues Verification & Handoff 2 (5u)"]
        G2{"Gate 2: Venues Tests Pass, PR Merged"}
        P8A --> G2
    end

    subgraph Milestone3["Milestone 3: Rankings & System Release (Nilakshi — 25 Units)"]
        H2["docs/handoffs/RANKINGS_MODULE_HANDOFF.md"]
        G2 --> H2
        H2 --> P8B["Phase 8B: Rankings Onboarding & Design (5u)"]
        P8B --> P9["Phase 9: Rankings ETL, SQL & UI (10u)"]
        P9 --> P10["Phase 10: System Integration & Regression (10u)"]
        G3{"Gate 3: All 20 SQL Queries Asserted, Release v1.0.0"}
        P10 --> G3
    end
```

---

## 10. COMPREHENSIVE RISK REGISTER & MITIGATION STRATEGY

| Risk ID | Identified Risk Description | Prob | Impact | Priority | Architectural Mitigation Strategy | Owner | Phase |
|---|---|:---:|:---:|:---:|---|:---:|:---:|
| `RSK-01` | **Sportradar API Expiry / Missing Key** | High | High | **P1** | Explicit `DEMO` mode serves verified synthetic fixtures from `tests/fixtures/` with prominent UI warning banner; `LIVE` mode fails fast on invalid credentials. | Devansh | Phase 2 |
| `RSK-02` | **API Rate-Limiting Violations (429)** | High | Med | **P2** | `SportradarClient` enforces minimum 1.0s interval pacing and applies exponential backoff retries. | Devansh | Phase 2 |
| `RSK-03` | **Database Syntax Dialect Incompatibilities** | Med | High | **P1** | Re-evaluated database strategy: recommend MySQL 8.0+ for submission, maintain SQLite for fast Pytest runs, implement dialect adapter in `DatabaseManager`. | Devansh / Mansi | Phase 6 |
| `RSK-04` | **Weekly Ranking Snapshot Collisions** | Med | High | **P2** | Phase 8B architectural decision: verify API availability before deciding between 6-column baseline vs. extended snapshot schema. | Nilakshi | Phase 8B |
| `RSK-05` | **Silent Synthetic Data Contamination** | Med | High | **P1** | Removed automatic mock fallback. Mode must be explicitly set via `COURTIQ_MODE=LIVE` or `COURTIQ_MODE=DEMO`. | Devansh | Phase 2 |
| `RSK-06` | **Streamlit Threading / SQLite Lock** | Low | Med | **P3** | SQLite configured with `check_same_thread=False` and short transaction scopes; read queries wrapped in Streamlit caching. | Devansh | Phase 2 |
| `RSK-07` | **Git Merge Conflicts Across Contributors** | Low | High | **P2** | Strict domain encapsulation: Mansi touches only `domains/venues/`; Nilakshi touches only `domains/rankings/`; core infrastructure is immutable. | All | Phases 6–10 |
| `RSK-08` | **Empty-State UI Exceptions Prior to Ingestion** | Med | Low | **P3** | All Streamlit pages implement empty-state checks with user callout boxes and one-click ingestion triggers. | All | Phases 4, 7, 9 |
| `RSK-09` | **Handoff Misinterpretation Across Agents** | Med | High | **P2** | Self-contained, copy-paste-ready handoff prompts with explicit file lists, test commands, and interface examples. | Mansi / Devansh | Phases 5, 8A |

---

## 11. TECHNICAL DECISIONS REQUIRING FORMAL ARCHITECTURAL APPROVAL

The following three architectural decisions remain clearly marked as **REQUIRING DEVANSH'S APPROVAL**:

1. **Primary Submission Database Selection:**  
   - *Recommendation:* Adopt **MySQL 8.0+** as the primary project database to achieve 100% compliance with Page 10 of the PDF guide and native `AUTO_INCREMENT` support, while retaining SQLite for fast, zero-dependency Pytest suite execution.  
   - *Status:* **PENDING DEVANSH'S APPROVAL.**
2. **Rankings Historical Snapshot Extension Adoption:**  
   - *Recommendation:* Preserve the PDF baseline 6-column schema initially. Evaluate live API payload in Phase 8B; adopt the extended `(snapshot_date, snapshot_year, snapshot_week)` schema only if verified from the live endpoint and approved.  
   - *Status:* **PENDING DEVANSH'S APPROVAL (Phase 8B Gate).**
3. **Multi-Domain Ingestion Architecture:**  
   - *Recommendation:* Provide standalone domain scripts (`ingest_competitions.py`, `ingest_venues.py`, `ingest_rankings.py`) alongside a master orchestrator (`scripts/ingest_all.py` / `IngestionRunner.ingest_all()`).  
   - *Status:* **PENDING DEVANSH'S APPROVAL.**

---

## 12. FINAL DEFINITION OF DONE (DoD)

The CourtIQ software product is officially deemed complete and ready for final capstone evaluation when all of the following criteria are met:

1. **Relational Schema Completeness:** All 6 normalized tables (`categories`, `competitions`, `complexes`, `venues`, `competitors`, `competitor_rankings`) created via sequential migrations (`001`, `002`, `003`) with active foreign-key constraints.
2. **20 Mandated SQL Queries Verified:** Every query specified in the project guide (Q1 through Q20) codified in `sql/queries/` and verified with automated assertions against test data.
3. **Explicit Operating Modes:** Seamless operation in `LIVE` mode (with verified Sportradar API key) or `DEMO` mode (with clearly badged synthetic fixtures), with zero silent data switching.
4. **Streamlit Multi-Page Experience:** Fully functional web application (`app.py`, `pages/1_Competitions.py`, `pages/2_Venues.py`, `pages/3_Rankings.py`) with responsive filters, interactive Plotly charts, data tables, and empty-state resilience.
5. **Automated Test Suite Pass Rate:** 100% pass rate across unit, integration, and regression test suites (`pytest tests -v`).
6. **Documentation Single Source of Truth:** Complete documentation repository including RTM, architecture, database ERD, data dictionary, guidelines, status telemetry, and both contributor handoff directives.
7. **Clean Version Control:** All branches merged to `main`, zero untracked artifacts, zero plain-text secrets, and synchronized with `https://github.com/Devansh54/CourtIQ.git`.
