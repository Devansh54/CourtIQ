# CourtIQ — Requirements Traceability Matrix (RTM)

**Project Name:** CourtIQ – Tennis Data & Analytics Explorer  
**Source Document:** `Game Analytics: Unlocking Tennis Data with SportRadar API (1)-2.pdf` (14 Pages)  
**Document Status:** Approved & Baseline Architected  
**Architecture Lead:** Devansh  

---

## 1. Executive Summary & Scope Boundary

The requirements below have been comprehensively extracted from the 14-page source project guide. Each requirement is assigned a unique identifier, categorized into explicit requirements, engineering prerequisites, or future enhancements, and traced directly to its architectural module, code implementation file, test specification, and module owner.

| Requirement Domain | Total Specs | Core Scope | Planned Owner |
|---|:---:|:---:|---|
| Shared Foundation & Infrastructure (INFRA) | 8 | Foundation | Devansh |
| Competitions & Categories Domain (COMP) | 14 | 50% Milestone | Devansh |
| Venues & Complexes Domain (VEN) | 12 | 25% Milestone | Venue & Complexes Module Owner |
| Doubles Competitor Rankings Domain (RNK) | 12 | 25% Milestone | Rankings & Analytics Module Owner |
| Streamlit Application & Visuals (UI) | 10 | Shared & Domain | Devansh (Shell + Comp) / Owners (Pages) |
| **Total Requirements** | **56** | **100%** | **Group Allocation: 50% / 25% / 25%** |

---

## 2. Shared Infrastructure Requirements (INFRA)

| Req ID | PDF Source Ref | Requirement Description | Implementation Target | Verification Method | Owner |
|---|---|---|---|---|---|
| `REQ-INFRA-01` | Page 2, 10 | Secure environment-based configuration management loading `.env` securely without committing secrets. | `src/courtiq/core/config.py` | Unit test with fixture `.env` | Devansh |
| `REQ-INFRA-02` | Page 2, 11 | Centralized database connection layer supporting ACID transactions, foreign keys, and parameterized SQL queries. | `src/courtiq/core/database.py` | DB connection & transaction unit tests | Devansh |
| `REQ-INFRA-03` | Page 2, 10, 11 | Robust Sportradar API client with rate-limiting (1 RPS trial), exponential backoff retries, and HTTP error handling. | `src/courtiq/core/api_client.py` | Mock API tests, rate limit tests | Devansh |
| `REQ-INFRA-04` | Page 10, 11 | Centralized structured logging and domain-specific exception hierarchies. | `src/courtiq/core/logging_config.py`, `src/courtiq/core/exceptions.py` | Unit test exception propagation | Devansh |
| `REQ-INFRA-05` | Page 2, 10 | Zero-dependency database migration system for reproducible DDL schema deployments. | `src/courtiq/core/database.py`, `sql/migrations/` | Migration execution test | Devansh |
| `REQ-INFRA-06` | Page 10, 11 | Common ingestion execution framework separating extraction, transformation, and storage. | `src/courtiq/ingestion/runner.py` | Ingestion pipeline test | Devansh |
| `REQ-INFRA-07` | Page 8, 10, 11 | Shared Streamlit application layout, CSS design system, header metrics, and navigation standards. | `app.py`, `src/courtiq/utils/formatting.py` | UI rendering & smoke tests | Devansh |
| `REQ-INFRA-08` | Page 10, 12 | Professional Git branching model, `.gitignore`, `.env.example`, and preserved source guide. | `.gitignore`, `.env.example`, `docs/reference/` | Git audit check | Devansh |

---

## 3. Competitions & Categories Domain Requirements (COMP) — Devansh (50%)

| Req ID | PDF Source Ref | Requirement Description | Implementation Target | Verification Method | Owner |
|---|---|---|---|---|---|
| `REQ-COMP-01` | Page 2 | Fetch raw competition payload from `https://developer.sportradar.com/tennis/reference/competitions`. | `src/courtiq/domains/competitions/extractor.py` | API client test & sample fixture | Devansh |
| `REQ-COMP-02` | Page 2 | Parse nested JSON into distinct normalized `categories` and `competitions` entities. | `src/courtiq/domains/competitions/transformer.py` | Schema parsing & data cleaning test | Devansh |
| `REQ-COMP-03` | Page 2 | Pydantic validation for Category (`category_id` PK, `category_name` NOT NULL). | `src/courtiq/domains/competitions/schemas.py` | Pydantic validation unit tests | Devansh |
| `REQ-COMP-04` | Page 2-3 | Pydantic validation for Competition (`competition_id` PK, `competition_name` NOT NULL, `parent_id` Nullable, `type` NOT NULL, `gender` NOT NULL, `category_id` FK). | `src/courtiq/domains/competitions/schemas.py` | Pydantic schema validation tests | Devansh |
| `REQ-COMP-05` | Page 2-3 | SQL Table creation for `categories` and `competitions` preserving PK, FK, and NOT NULL constraints. | `sql/migrations/001_competitions.sql` | DDL execution & FK constraint test | Devansh |
| `REQ-COMP-06` | Page 2-3 | Idempotent upsert/insertion of categories and competitions preventing duplicate records. | `src/courtiq/domains/competitions/repository.py` | Repetitive ingestion test | Devansh |
| `REQ-COMP-07` | Page 3 (Q1) | SQL Query 1: List all competitions along with their category name. | `sql/queries/competitions/q1_list_with_category.sql` | SQL verification test | Devansh |
| `REQ-COMP-08` | Page 3 (Q2) | SQL Query 2: Count the number of competitions in each category. | `sql/queries/competitions/q2_count_by_category.sql` | SQL verification test | Devansh |
| `REQ-COMP-09` | Page 4 (Q3) | SQL Query 3: Find all competitions of type 'doubles'. | `sql/queries/competitions/q3_doubles_competitions.sql` | SQL verification test | Devansh |
| `REQ-COMP-10` | Page 4 (Q4) | SQL Query 4: Get competitions that belong to a specific category (e.g., 'ITF Men'). | `sql/queries/competitions/q4_by_specific_category.sql` | SQL verification test | Devansh |
| `REQ-COMP-11` | Page 4 (Q5) | SQL Query 5: Identify parent competitions and their sub-competitions. | `sql/queries/competitions/q5_parent_sub_hierarchy.sql` | SQL verification test | Devansh |
| `REQ-COMP-12` | Page 4 (Q6) | SQL Query 6: Analyze the distribution of competition types by category. | `sql/queries/competitions/q6_type_distribution_by_category.sql` | SQL verification test | Devansh |
| `REQ-COMP-13` | Page 4 (Q7) | SQL Query 7: List all competitions with no parent (top-level competitions). | `sql/queries/competitions/q7_top_level_competitions.sql` | SQL verification test | Devansh |
| `REQ-COMP-14` | Page 8, 10 | Streamlit Competitions explorer with hierarchy tree, category filters, type/gender distribution charts, and data tables. | `pages/1_Competitions.py`, `src/courtiq/domains/competitions/analytics.py` | Streamlit component rendering test | Devansh |

---

## 4. Venues & Complexes Domain Requirements (VEN) — Venue & Complexes Module Owner (25%)

| Req ID | PDF Source Ref | Requirement Description | Implementation Target | Verification Method | Owner |
|---|---|---|---|---|---|
| `REQ-VEN-01` | Page 4 | Fetch raw complexes & venues payload from `https://developer.sportradar.com/tennis/reference/complexes`. | `src/courtiq/domains/venues/extractor.py` | API client test & sample fixture | Venue & Complexes Module Owner |
| `REQ-VEN-02` | Page 4-5 | Parse nested JSON into normalized `complexes` and `venues` entities. | `src/courtiq/domains/venues/transformer.py` | Schema parsing & data cleaning test | Venue & Complexes Module Owner |
| `REQ-VEN-03` | Page 4 | Pydantic validation for Complex (`complex_id` PK, `complex_name` NOT NULL). | `src/courtiq/domains/venues/schemas.py` | Pydantic validation unit tests | Venue & Complexes Module Owner |
| `REQ-VEN-04` | Page 4-5 | Pydantic validation for Venue (`venue_id` PK, `venue_name`, `city_name`, `country_name`, `country_code` CHAR(3), `timezone`, `complex_id` FK). | `src/courtiq/domains/venues/schemas.py` | Pydantic schema validation tests | Venue & Complexes Module Owner |
| `REQ-VEN-05` | Page 4-5 | SQL Table creation for `complexes` and `venues` preserving foreign keys. | `sql/migrations/002_venues.sql` | DDL execution & FK constraint test | Venue & Complexes Module Owner |
| `REQ-VEN-06` | Page 5 (Q1) | SQL Query 1: List all venues along with their associated complex name. | `sql/queries/venues/q1_venues_with_complex.sql` | SQL verification test | Venue & Complexes Module Owner |
| `REQ-VEN-07` | Page 5 (Q2) | SQL Query 2: Count the number of venues in each complex. | `sql/queries/venues/q2_venues_count_per_complex.sql` | SQL verification test | Venue & Complexes Module Owner |
| `REQ-VEN-08` | Page 5 (Q3) | SQL Query 3: Get details of venues in a specific country (e.g., 'Chile'). | `sql/queries/venues/q3_venues_by_country.sql` | SQL verification test | Venue & Complexes Module Owner |
| `REQ-VEN-09` | Page 5 (Q4) | SQL Query 4: Identify all venues and their timezones. | `sql/queries/venues/q4_venues_and_timezones.sql` | SQL verification test | Venue & Complexes Module Owner |
| `REQ-VEN-10` | Page 5 (Q5) | SQL Query 5: Find complexes that have more than one venue. | `sql/queries/venues/q5_multi_venue_complexes.sql` | SQL verification test | Venue & Complexes Module Owner |
| `REQ-VEN-11` | Page 5 (Q6, Q7) | SQL Query 6 & 7: List venues grouped by country; Find all venues for a specific complex (e.g., 'Nacional'). | `sql/queries/venues/q6_venues_by_country_group.sql`, `sql/queries/venues/q7_venues_for_specific_complex.sql` | SQL verification test | Venue & Complexes Module Owner |
| `REQ-VEN-12` | Page 8, 10 | Streamlit Venues explorer with country filters, timezone breakdowns, multi-venue complex analyzer, and charts. | `pages/2_Venues.py`, `src/courtiq/domains/venues/analytics.py` | Streamlit component rendering test | Venue & Complexes Module Owner |

---

## 5. Doubles Competitor Rankings Domain Requirements (RNK) — Rankings & Analytics Module Owner (25%)

| Req ID | PDF Source Ref | Requirement Description | Implementation Target | Verification Method | Owner |
|---|---|---|---|---|---|
| `REQ-RNK-01` | Page 6 | Fetch doubles competitor rankings from `https://developer.sportradar.com/tennis/reference/doubles-competitor-rankings`. | `src/courtiq/domains/rankings/extractor.py` | API client test & sample fixture | Rankings & Analytics Module Owner |
| `REQ-RNK-02` | Page 6-7 | Parse nested ranking JSON into normalized `competitors` and `competitor_rankings` entities. | `src/courtiq/domains/rankings/transformer.py` | Schema parsing & data cleaning test | Rankings & Analytics Module Owner |
| `REQ-RNK-03` | Page 7 | Pydantic validation for Competitor (`competitor_id` PK, `name`, `country`, `country_code` CHAR(3), `abbreviation`). | `src/courtiq/domains/rankings/schemas.py` | Pydantic validation unit tests | Rankings & Analytics Module Owner |
| `REQ-RNK-04` | Page 6-7 | Pydantic validation for Ranking (`rank_id` PK AUTO_INCREMENT, `rank`, `movement`, `points`, `competitions_played`, `competitor_id` FK). | `src/courtiq/domains/rankings/schemas.py` | Pydantic schema validation tests | Rankings & Analytics Module Owner |
| `REQ-RNK-05` | Page 6-7 | SQL Table creation for `competitors` and `competitor_rankings` preserving foreign keys. | `sql/migrations/003_rankings.sql` | DDL execution & FK constraint test | Rankings & Analytics Module Owner |
| `REQ-RNK-06` | Page 7 (Q1) | SQL Query 1: Get all competitors with their rank and points. | `sql/queries/rankings/q1_competitors_rank_points.sql` | SQL verification test | Rankings & Analytics Module Owner |
| `REQ-RNK-07` | Page 7 (Q2) | SQL Query 2: Find competitors ranked in the top 5. | `sql/queries/rankings/q2_top_5_competitors.sql` | SQL verification test | Rankings & Analytics Module Owner |
| `REQ-RNK-08` | Page 8 (Q3) | SQL Query 3: List competitors with no rank movement (stable rank). | `sql/queries/rankings/q3_stable_rank_competitors.sql` | SQL verification test | Rankings & Analytics Module Owner |
| `REQ-RNK-09` | Page 8 (Q4) | SQL Query 4: Get total points of competitors from a specific country (e.g., 'Croatia'). | `sql/queries/rankings/q4_points_by_country.sql` | SQL verification test | Rankings & Analytics Module Owner |
| `REQ-RNK-10` | Page 8 (Q5) | SQL Query 5: Count the number of competitors per country. | `sql/queries/rankings/q5_competitors_per_country.sql` | SQL verification test | Rankings & Analytics Module Owner |
| `REQ-RNK-11` | Page 8 (Q6) | SQL Query 6: Find competitors with highest points in current ranking data. | `sql/queries/rankings/q6_highest_points_competitors.sql` | SQL verification test | Rankings & Analytics Module Owner |
| `REQ-RNK-12` | Page 8, 10 | Streamlit Rankings explorer with search, leaderboard, country-wise distribution, rank movement tags, and detail modal. | `pages/3_Rankings.py`, `src/courtiq/domains/rankings/analytics.py` | Streamlit component rendering test | Rankings & Analytics Module Owner |

---

## 6. Streamlit User Interface & Dashboard Requirements (UI)

| Req ID | PDF Source Ref | Feature Description | Implementation Target | Verification Method | Planned Owner |
|---|---|---|---|---|---|
| `REQ-UI-01` | Page 8 | Homepage Dashboard with top KPIs (Total Competitors, Represented Countries, Top Score, Total Venues, Total Competitions). | `app.py` | UI render & state verification | Devansh |
| `REQ-UI-02` | Page 8 | Real-time SQL database connectivity for all Streamlit views with caching. | `src/courtiq/core/database.py`, `app.py` | Session state & caching test | Devansh |
| `REQ-UI-03` | Page 8-9 | Custom CSS styling for professional sports analytics look & feel. | `src/courtiq/utils/formatting.py`, `app.py` | Visual inspection | Devansh |
| `REQ-UI-04` | Page 8 | Competitions Explorer with hierarchical navigation, category filters, and interactive tables. | `pages/1_Competitions.py` | Interactive filter test | Devansh |
| `REQ-UI-05` | Page 8 | Venues & Complexes Explorer with country dropdowns, timezone analytics, and complex drilldown. | `pages/2_Venues.py` | Interactive filter test | Venue & Complexes Module Owner |
| `REQ-UI-06` | Page 8 | Rankings Explorer with player search, top 5 leaderboards, and country aggregations. | `pages/3_Rankings.py` | Interactive filter test | Rankings & Analytics Module Owner |
| `REQ-UI-07` | Page 8-10 | Graceful empty-state and error-state displays when database tables are unpopulated or API is unconfigured. | All Streamlit pages | Empty DB test | All Module Owners |
