# CourtIQ — Relational Data Dictionary

**Product Name:** CourtIQ – Tennis Data & Analytics Explorer  
**Version:** 1.0.0  
**Lead Architect:** Devansh  

---

## 1. Schema Overview

The CourtIQ data model consists of 6 tables across 3 distinct sports analytics domains. All string primary keys utilize Sportradar Uniform Resource Names (`sr:category:*`, `sr:competition:*`, `sr:complex:*`, `sr:venue:*`, `sr:competitor:*`).

---

## 2. Table: `categories`
- **Domain:** Competitions & Categories
- **Owner:** Devansh
- **Purpose:** Stores top-level governing bodies and category classifications for tennis competitions.

| Column | Data Type | Nullable | Key | Default | Example Value | Description |
|---|---|:---:|:---:|---|---|---|
| `category_id` | VARCHAR(50) | NO | PK | - | `sr:category:1` | Unique Sportradar category identifier. |
| `category_name` | VARCHAR(100) | NO | - | - | `ATP` | Display title of category (e.g. ATP, WTA, ITF Men). |

---

## 3. Table: `competitions`
- **Domain:** Competitions & Categories
- **Owner:** Devansh
- **Purpose:** Stores specific tournaments, circuits, and events, supporting multi-level parent-child hierarchies.

| Column | Data Type | Nullable | Key | Default | Example Value | Description |
|---|---|:---:|:---:|---|---|---|
| `competition_id` | VARCHAR(50) | NO | PK | - | `sr:competition:101` | Unique Sportradar tournament identifier. |
| `competition_name` | VARCHAR(100) | NO | - | - | `ATP Australian Open` | Official event title. |
| `parent_id` | VARCHAR(50) | YES | FK | NULL | `sr:competition:100` | Self-referencing ID of parent competition. |
| `type` | VARCHAR(20) | NO | - | - | `singles` | Competition format (`singles`, `doubles`, `mixed`). |
| `gender` | VARCHAR(10) | NO | - | - | `men` | Participant gender (`men`, `women`, `mixed`). |
| `category_id` | VARCHAR(50) | NO | FK | - | `sr:category:1` | Foreign key referencing `categories.category_id`. |

---

## 4. Table: `complexes`
- **Domain:** Complexes & Venues
- **Owner:** Venue & Complexes Module Owner
- **Purpose:** Stores physical sports facilities and tournament grounds.

| Column | Data Type | Nullable | Key | Default | Example Value | Description |
|---|---|:---:|:---:|---|---|---|
| `complex_id` | VARCHAR(50) | NO | PK | - | `sr:complex:12` | Unique Sportradar sports complex ID. |
| `complex_name` | VARCHAR(100) | NO | - | - | `Melbourne Park` | Name of the multi-venue sports facility. |

---

## 5. Table: `venues`
- **Domain:** Complexes & Venues
- **Owner:** Venue & Complexes Module Owner
- **Purpose:** Stores specific playing stadia, arenas, and courts tied to a sports complex.

| Column | Data Type | Nullable | Key | Default | Example Value | Description |
|---|---|:---:|:---:|---|---|---|
| `venue_id` | VARCHAR(50) | NO | PK | - | `sr:venue:34` | Unique Sportradar venue identifier. |
| `venue_name` | VARCHAR(100) | NO | - | - | `Rod Laver Arena` | Name of the court or stadium. |
| `city_name` | VARCHAR(100) | NO | - | - | `Melbourne` | Host city name. |
| `country_name` | VARCHAR(100) | NO | - | - | `Australia` | Host country name. |
| `country_code` | CHAR(3) | NO | - | - | `AUS` | ISO 3166-1 alpha-3 code. |
| `timezone` | VARCHAR(100) | NO | - | - | `Australia/Melbourne`| Standard IANA timezone string. |
| `complex_id` | VARCHAR(50) | NO | FK | - | `sr:complex:12` | Foreign key referencing `complexes.complex_id`. |

---

## 6. Table: `competitors`
- **Domain:** Doubles Competitor Rankings
- **Owner:** Rankings & Analytics Module Owner
- **Purpose:** Stores individual tennis competitor biographical and country information.

| Column | Data Type | Nullable | Key | Default | Example Value | Description |
|---|---|:---:|:---:|---|---|---|
| `competitor_id` | VARCHAR(50) | NO | PK | - | `sr:competitor:101` | Unique Sportradar competitor identifier. |
| `name` | VARCHAR(100) | NO | - | - | `Granollers, Marcel`| Competitor's official full name. |
| `country` | VARCHAR(100) | NO | - | - | `Spain` | Competitor's represented country. |
| `country_code` | CHAR(3) | NO | - | - | `ESP` | ISO 3166-1 alpha-3 nationality code. |
| `abbreviation` | VARCHAR(10) | NO | - | - | `GRA` | Broadcast scoreboard abbreviation. |

---

## 7. Table: `competitor_rankings`
- **Domain:** Doubles Competitor Rankings
- **Owner:** Rankings & Analytics Module Owner
- **Purpose:** Stores doubles ranking positions, week-over-week movements, and accumulated points.

| Column | Data Type | Nullable | Key | Default | Example Value | Description |
|---|---|:---:|:---:|---|---|---|
| `rank_id` | INTEGER | NO | PK | AUTOINCREMENT | `1` | Surrogate auto-incrementing primary key. |
| `rank` | INT | NO | - | - | `1` | Official world doubles ranking standing. |
| `movement` | INT | NO | - | - | `0` | Rank change relative to prior week. |
| `points` | INT | NO | - | - | `7820` | Total ranking points. |
| `competitions_played` | INT | NO | - | - | `22` | Tournaments played in current ranking cycle. |
| `competitor_id` | VARCHAR(50) | NO | FK | - | `sr:competitor:101` | Foreign key referencing `competitors.competitor_id`. |
