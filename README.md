# CourtIQ

### Tennis Data & Analytics Explorer

**Explore Competitions. Analyse Rankings. Discover Tennis.**

CourtIQ is a Python-based tennis data exploration and analytics application built around the [Sportradar Tennis API](https://developer.sportradar.com/tennis/reference/tennis-overview). It brings together structured information about tennis competitions, sports complexes and venues, and doubles competitor rankings, with the aim of making that data easier to explore and analyse.

The project combines API-based data collection, data validation and transformation, relational storage, SQL analytics, and an interactive [Streamlit](https://streamlit.io/) interface.

## Project domains

CourtIQ is organised around three related areas of tennis data.

### Competitions and categories

Explore competition metadata and how competitions are organised, including:

- Competition names, categories, formats, and gender classifications.
- Parent competitions and their sub-competition relationships.
- Competition counts and format distributions across categories.
- Filtering and searching by competition attributes.

### Complexes and venues

Explore tennis facilities and their location information, including:

- Sports complexes and the venues associated with them.
- Venue names, cities, and countries.
- Country codes and time zones.
- Venue counts by complex and country.

### Doubles competitor rankings

Explore doubles ranking information and competitor metadata, including:

- Competitor names and countries.
- Ranking positions and movement.
- Ranking points and competitions played.
- Top-ranked competitors and country-level summaries.

## Data workflow

The application separates data collection and processing from persistence and presentation.

```text
Sportradar Tennis API
        |
        v
Shared API client
        |
        v
Domain-specific extraction
        |
        v
Transformation and validation
        |
        v
Relational SQL database
        |
        v
Repositories and analytical queries
        |
        v
Streamlit application
```

The codebase uses shared infrastructure for configuration, API communication, database access, logging, and exceptions. Domain-specific modules contain the data extraction, transformation, persistence, and analytical logic for each subject area.

## Technology stack

| Area | Technology |
|---|---|
| Language | Python 3.10+ |
| Data provider | Sportradar Tennis API v3 |
| HTTP client | Requests |
| Data processing | Pandas |
| Data validation | Pydantic |
| Relational database | SQLite |
| Application interface | Streamlit |
| Visualisation | Plotly |
| Testing | Pytest |

## Getting started

### Prerequisites

- Python 3.10 or later
- Git
- A Sportradar Tennis API key for live API access

### 1. Clone the repository

```bash
git clone https://github.com/Devansh54/CourtIQ.git
cd CourtIQ
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

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

Create a local `.env` file from the example template.

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux**

```bash
cp .env.example .env
```

Add your Sportradar API key to `.env`:

```dotenv
SPORTRADAR_API_KEY=your_api_key_here
```

The example file also contains settings for the API base URL, request timeout, request pacing, retry behaviour, database location, and logging.

**Keep credentials private.** Do not commit `.env`, API keys, or other secrets. The repository includes `.env.example` for configuration reference.

### 5. Ingest competition data

The competition ingestion script applies pending database migrations and runs the competitions data pipeline:

```bash
python scripts/ingest_competitions.py
```

The current API client can use bundled synthetic fixtures when no usable API key is configured, and may fall back to fixtures after repeated network failures. Fixture-backed records are sample data; they are not live Sportradar data.

### 6. Run the application

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit, usually <http://localhost:8501>.

### 7. Run the tests

```bash
python -m pytest tests -v
```

## Database

The current database manager uses SQLite. By default, the database file is stored at:

```text
data/courtiq.db
```

Database schema changes are maintained as ordered SQL migration files in `sql/migrations/`. The data model is organised around these related entities:

| Data area | Tables | Relationship |
|---|---|---|
| Competitions | `categories`, `competitions` | A category can contain multiple competitions; competitions can reference a parent competition. |
| Venues | `complexes`, `venues` | A complex can contain multiple venues. |
| Rankings | `competitors`, `competitor_rankings` | A competitor can have associated ranking records. |

For table definitions, constraints, and the entity-relationship diagram, see [Database Design](docs/DATABASE_DESIGN.md).

## Repository structure

```text
CourtIQ/
├── app.py                         # Streamlit application entry point
├── pages/                         # Streamlit pages
├── src/
│   └── courtiq/
│       ├── core/                  # Configuration, API client and database access
│       ├── domains/
│       │   ├── competitions/      # Competition data and analytics
│       │   ├── venues/             # Complex and venue domain
│       │   └── rankings/           # Competitor ranking domain
│       ├── ingestion/              # Data ingestion orchestration
│       └── utils/                  # Shared application utilities
├── sql/
│   ├── migrations/                # Database schema migrations
│   └── queries/                   # Domain-specific analytical SQL
├── scripts/                       # Command-line utilities
├── tests/
│   ├── fixtures/                  # Sample API payloads
│   ├── unit/                      # Unit tests
│   └── integration/               # Integration tests
└── docs/                           # Project and technical documentation
```

## API references

CourtIQ uses the Sportradar Tennis API. Consult the official documentation for endpoint specifications, response formats, authentication, and subscription requirements:

- [Sportradar Tennis API overview](https://developer.sportradar.com/tennis/reference/tennis-overview)
- [Competitions endpoint](https://developer.sportradar.com/tennis/reference/competitions)
- [Complexes endpoint](https://developer.sportradar.com/tennis/reference/complexes)
- [Doubles competitor rankings endpoint](https://developer.sportradar.com/tennis/reference/doubles-competitor-rankings)

API availability, request limits, and quotas depend on the Sportradar plan associated with the API key.

## Project documentation

Further technical details are maintained in the `docs/` directory:

- [Project overview](docs/PROJECT_OVERVIEW.md)
- [Requirements](docs/REQUIREMENTS.md)
- [System architecture](docs/ARCHITECTURE.md)
- [Database design](docs/DATABASE_DESIGN.md)
- [API documentation](docs/API_DOCUMENTATION.md)
- [Data dictionary](docs/DATA_DICTIONARY.md)
- [Development guidelines](docs/DEVELOPMENT_GUIDELINES.md)
- [Original project guide](docs/reference/PROJECT_GUIDE.pdf)

## License

The project metadata identifies CourtIQ as proprietary. Public repository visibility does not grant permission to reuse, modify, or redistribute the code. Contact the repository owner for permission.
