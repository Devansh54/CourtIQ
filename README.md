# CourtIQ

### Tennis Data & Analytics Explorer

**Explore Competitions. Analyse Rankings. Discover Tennis.**

CourtIQ is a Python-based tennis data exploration and analytics application built around the [Sportradar Tennis API](https://developer.sportradar.com/tennis/reference/tennis-overview). It brings together structured information about tennis competitions, sports complexes and venues, and doubles competitor rankings, with the aim of making that data easier to explore and analyse.

The project combines API-based data collection, data validation and transformation, relational storage with **PostgreSQL 18**, SQL analytics, and an interactive [Streamlit](https://streamlit.io/) interface.

---

## Project domains

CourtIQ is organised around three related areas of tennis data:

### 1. Competitions and categories (Devansh — 50%)
Explore competition metadata and how competitions are organised, including:
- Competition names, categories, formats, and gender classifications.
- Parent competitions and their sub-competition relationships.
- Competition counts and format distributions across categories.
- Filtering, searching, and execution of all 7 required analytical queries.

### 2. Complexes and venues (Mansi — 25%)
Explore tennis facilities and their location information, including:
- Sports complexes and the venues associated with them.
- Venue names, cities, and countries.
- Country codes and time zones.
- Venue counts by complex and country.

### 3. Doubles competitor rankings (Nilakshi — 25%)
Explore doubles ranking information and competitor metadata, including:
- Competitor names and countries.
- Ranking positions and movement.
- Ranking points and competitions played.
- Top-ranked competitors and country-level summaries.

---

## Data workflow

The application separates data collection and processing from persistence and presentation:

```text
Sportradar Tennis API (or Synthetic Demo Fixtures)
        │
        ▼
Shared API Client (Rate-limited, retry backoff)
        │
        ▼
Domain-Specific Extraction (Pydantic models)
        │
        ▼
Transformation & Validation (Relational normalization)
        │
        ▼
PostgreSQL 18 Relational Database (SQLAlchemy 2.x Core & QueuePool)
        │
        ▼
Repositories & Parameterized Analytical SQL Queries
        │
        ▼
Interactive Streamlit Dashboard & Plotly Visualizations
```

---

## Technology stack

| Area | Technology | Purpose |
|---|---|---|
| Language | Python 3.10+ (Tested on 3.12) | Core programming language |
| Data provider | Sportradar Tennis API v3 | Official Tennis API data |
| Relational database | PostgreSQL 18 | Primary database (Docker Compose or native) |
| Fallback database | SQLite | Offline environments & isolated unit test suites |
| ORM / SQL engine | SQLAlchemy 2.x Core | Connection pooling (`QueuePool`), transactional contexts |
| Database driver | Psycopg 3 (`psycopg[binary]>=3.1.18`) | High-performance PostgreSQL connector |
| Migrations | Alembic (`>=1.13.0`) | Repeatable DDL schema migrations |
| Containerisation | Docker Compose | One-command PostgreSQL service provisioning |
| Data processing | Pandas | Relational querying and DataFrame analytics |
| Data validation | Pydantic v2 | Strict JSON schema parsing and entity validation |
| Application interface | Streamlit | Multi-page interactive analytics portal |
| Visualisation | Plotly | Dynamic bar charts, sunbursts, and distributions |
| Testing | Pytest | Unit, pipeline, and concurrency test suites |

---

## Getting started

### Prerequisites
- Python 3.10 or later
- Git
- Docker & Docker Compose (recommended for PostgreSQL), or a local PostgreSQL 18 installation
- A Sportradar Tennis API key (optional; system includes DEMO mode with bundled fixtures)

### 1. Clone the repository

```bash
git clone https://github.com/Devansh54/CourtIQ.git
cd CourtIQ
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create your local `.env` configuration file from the template:

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

Open `.env` and configure your settings:
- **Mandatory PostgreSQL Passwords:** Replace the placeholder values for `POSTGRES_SUPERUSER_PASSWORD`, `COURTIQ_MIGRATOR_PASSWORD`, and `COURTIQ_APP_PASSWORD` with your own secure local credentials. Ensure the password values embedded in the connection strings match their respective role passwords:
  - `DATABASE_URL=postgresql+psycopg://courtiq_app:<COURTIQ_APP_PASSWORD>@127.0.0.1:5432/courtiq`
  - `MIGRATION_DATABASE_URL=postgresql+psycopg://courtiq_migrator:<COURTIQ_MIGRATOR_PASSWORD>@127.0.0.1:5432/courtiq`
  - `TEST_DATABASE_URL=postgresql+psycopg://courtiq_migrator:<COURTIQ_MIGRATOR_PASSWORD>@127.0.0.1:5432/courtiq_test`
- **Operating Mode:**
  - To run in **DEMO mode** (default), leave `COURTIQ_MODE=DEMO`. CourtIQ will load verified synthetic fixtures from `tests/fixtures/` without making external API requests or requiring a Sportradar API key.
  - To run in **LIVE mode**, set `COURTIQ_MODE=LIVE` and supply your valid `SPORTRADAR_API_KEY`.
- *Never commit your `.env` file to version control.*

### 5. Start PostgreSQL with Docker Compose

Only after `.env` has been configured with the required password variables, launch the PostgreSQL 18 container with persistent storage and pre-configured least-privilege roles:

```bash
docker compose up -d
```

Verify that the container is healthy:
```bash
docker compose ps
```

*(For manual PostgreSQL installation or troubleshooting, see the [PostgreSQL Setup Guide](docs/POSTGRESQL_SETUP.md)).*

### 6. Run database migrations

Apply database schema tables using Alembic:

```bash
alembic upgrade head
```

### 7. (Optional) Migrate historical SQLite data

If upgrading an existing installation with data in `data/courtiq.db`, transfer all records into PostgreSQL:

```bash
# Preview records to be transferred (safe dry run)
python scripts/migrate_sqlite_to_postgres.py --dry-run

# Execute data migration with automated SQLite backup
python scripts/migrate_sqlite_to_postgres.py --apply
```

### 8. Ingest competition data

Run the ingestion pipeline to populate tournament categories and competitions:

```bash
python scripts/ingest_competitions.py
```

### 9. Run the Streamlit application

```bash
streamlit run app.py
```

Open the local URL in your browser: <http://localhost:8501>.

### 10. Run automated tests

Execute the unit, integration, and concurrency test suites:

```bash
python -m pytest tests -v
```

---

## Database architecture & security

CourtIQ uses **PostgreSQL 18** as its primary relational engine, configured with strict least-privilege security roles:

- `courtiq_migrator`: Dedicated DDL role used by Alembic migrations to create and alter schema tables.
- `courtiq_app`: Restricted DML role used at application runtime for `SELECT`, `INSERT`, `UPDATE`, `DELETE` queries. This role cannot perform destructive DDL actions like `DROP` or `ALTER TABLE`.
- **Connection Pooling:** Managed via SQLAlchemy 2.x `QueuePool` with health pre-pinging (`pool_pre_ping=True`) and connection recycling to handle concurrent Streamlit user traffic without deadlocks.

| Data Area | Tables | Key Relationships |
|---|---|---|
| Competitions | `categories`, `competitions` | Self-referencing foreign key for parent/child tournament hierarchies. |
| Venues | `complexes`, `venues` | A complex contains multiple individual venues/courts. |
| Rankings | `competitors`, `competitor_rankings` | Weekly ranking snapshots linked to competitor records. |

For full table schemas, column data types, indexes, and constraints, see [Database Design](docs/DATABASE_DESIGN.md) and [PostgreSQL Setup](docs/POSTGRESQL_SETUP.md).

---

## Repository structure

```text
CourtIQ/
├── app.py                         # Streamlit application entry point & dashboard
├── pages/                         # Streamlit domain exploration pages
│   ├── 1_Competitions.py          # Competitions explorer (Devansh)
│   ├── 2_Venues.py                # Venues explorer (Mansi)
│   └── 3_Rankings.py              # Rankings explorer (Nilakshi)
├── compose.yaml                   # Docker Compose specification for PostgreSQL 18
├── alembic.ini                    # Alembic migration configuration
├── alembic/                       # Alembic version migration scripts
│   ├── env.py                     # Dynamic database URL resolution & migration runner
│   └── versions/                  # Revision scripts (0001_initial_competitions.py)
├── docker/
│   └── postgres/init/             # Container role initialization SQL (01_init_roles.sql)
├── src/
│   └── courtiq/
│       ├── core/                  # Configuration, database manager, pooling, API client
│       ├── domains/
│       │   ├── competitions/      # Competitions schemas, extractor, repo, analytics
│       │   ├── venues/            # Venues domain scaffolding (ready for Mansi)
│       │   └── rankings/          # Rankings domain scaffolding (ready for Nilakshi)
│       ├── ingestion/             # Pipeline orchestration runner
│       └── utils/                 # Visual styling, formatting, CSS
├── sql/
│   ├── migrations/                # Historical SQL migration reference
│   └── queries/competitions/      # Project guide mandated SQL queries (q1–q7)
├── scripts/
│   ├── ingest_competitions.py     # Competitions ingestion executable CLI
│   └── migrate_sqlite_to_postgres.py # Safe SQLite-to-PostgreSQL migration utility
├── tests/
│   ├── fixtures/                  # Offline sample API JSON payloads
│   ├── unit/                      # Database, config, schema, repository unit tests
│   ├── integration/               # End-to-end pipeline integration tests
│   └── concurrency/               # Multi-threaded connection pool load tests
└── docs/                          # Comprehensive technical and architectural documentation
    ├── POSTGRESQL_SETUP.md        # Detailed PostgreSQL & Docker configuration guide
    ├── ARCHITECTURE.md            # Target system architecture and data flows
    ├── DATABASE_DESIGN.md         # Database schema, normalization, and constraints
    ├── DEVELOPMENT_GUIDELINES.md  # Contributor guidelines for Mansi & Nilakshi
    ├── IMPLEMENTATION_STATUS.md   # Current implementation tracking & milestones
    └── TEAM_WORK_ALLOCATION.md    # 50% / 25% / 25% workload distribution agreement
```

---

## Project documentation

Further technical details are maintained in the `docs/` directory:

- [PostgreSQL Setup & Migration Guide](docs/POSTGRESQL_SETUP.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [Database Design](docs/DATABASE_DESIGN.md)
- [Development Guidelines](docs/DEVELOPMENT_GUIDELINES.md)
- [Implementation Status](docs/IMPLEMENTATION_STATUS.md)
- [Team Work Allocation](docs/TEAM_WORK_ALLOCATION.md)
- [Project Overview](docs/PROJECT_OVERVIEW.md)
- [Requirements](docs/REQUIREMENTS.md)
- [Data Dictionary](docs/DATA_DICTIONARY.md)

---

## License

The project metadata identifies CourtIQ as proprietary. Public repository visibility does not grant permission to reuse, modify, or redistribute the code. Contact the repository owner for permission.
