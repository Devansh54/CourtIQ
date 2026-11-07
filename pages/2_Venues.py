"""CourtIQ: Complexes & Venues Explorer.

Domain Contributor: Mansi (Venue & Complexes Module Owner — 25% Workload Allocation)
Reference: docs/handoffs/VENUES_MODULE_HANDOFF.md
"""

import sys
from pathlib import Path

# Add src to sys.path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

import streamlit as st
from courtiq.utils.formatting import apply_custom_css, render_section_header

st.set_page_config(page_title="Venues Explorer | CourtIQ", page_icon="🏟️", layout="wide")
apply_custom_css()

st.title("🏟️ Tennis Complexes & Venues Explorer")
st.caption("Module Owner: Mansi (Venue & Complexes Module Owner — 25% Workload Allocation)")

st.info("""
### 📋 Module Status: Ready for Venue & Complexes Module Owner (Mansi)
This domain is architecturally designed and isolated for implementation by **Mansi** (Venue & Complexes Module Owner).
The PostgreSQL 18 relational foundation, connection pooling (`QueuePool`), Alembic migration framework, dual-mode Sportradar API client, and shared repository interfaces have been established and verified by Devansh.
""")

render_section_header("Module Responsibilities & Requirements", "Extracted from Project Guide (PDF Pages 4-5) & PostgreSQL 18 Design")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Database Schemas (PostgreSQL 18)
    - **`complexes` Table:** `complex_id` VARCHAR(50) PK, `complex_name` VARCHAR(100) NOT NULL.
    - **`venues` Table:** `venue_id` VARCHAR(50) PK, `venue_name` VARCHAR(100) NOT NULL, `city_name` VARCHAR(100) NOT NULL, `country_name` VARCHAR(100) NOT NULL, `country_code` CHAR(3) NOT NULL, `timezone` VARCHAR(100) NOT NULL, `complex_id` VARCHAR(50) FK REFERENCES complexes(complex_id) ON DELETE CASCADE.
    - **PostgreSQL Indexes:** `idx_venues_complex_id`, `idx_venues_country_code`, `idx_venues_city_name`.
    
    #### Required Analytical SQL Queries
    1. List all venues along with their associated complex name.
    2. Count the number of venues in each complex.
    3. Get details of venues in a specific country (e.g., Chile).
    4. Identify all venues and their timezones.
    5. Find complexes that have more than one venue.
    6. List venues grouped by country.
    7. Find all venues for a specific complex (e.g., Nacional).
    """)

with col2:
    st.markdown("""
    #### Deliverables Checklist for Module Owner (Mansi)
    - [ ] `alembic/versions/0002_venues.py` (Alembic DDL migration chained to `0001_initial_competitions`)
    - [ ] `src/courtiq/domains/venues/schemas.py` (Pydantic validation models)
    - [ ] `src/courtiq/domains/venues/extractor.py` (Sportradar complexes extraction)
    - [ ] `src/courtiq/domains/venues/transformer.py` (Payload normalizer)
    - [ ] `src/courtiq/domains/venues/repository.py` (PostgreSQL upserts with `ON CONFLICT` & query runner)
    - [ ] `src/courtiq/domains/venues/analytics.py` (Plotly charts & KPI summaries)
    - [ ] `sql/queries/venues/` (7 PostgreSQL query files using named parameters)
    - [ ] Full interactive Streamlit explorer UI on this page (`pages/2_Venues.py`)
    - [ ] Unit & Integration Tests in `tests/unit/venues/` and `tests/integration/`
    - [ ] Subsequent Handoff Directive: `docs/handoffs/RANKINGS_MODULE_HANDOFF.md`
    """)

st.markdown("---")
st.markdown("👉 **Please consult the comprehensive handoff guide:** `docs/handoffs/VENUES_MODULE_HANDOFF.md`")
