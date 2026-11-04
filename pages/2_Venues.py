"""CourtIQ: Complexes & Venues Explorer.

Domain Contributor: Venue & Complexes Module Owner (25% Contribution)
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
st.caption("Module Owner: Venue & Complexes Module Owner (25% Workload Allocation)")

st.info("""
### 📋 Module Status: Ready for Venue & Complexes Module Owner
This domain is architecturally designed and isolated for implementation by the **Venue & Complexes Module Owner**.
The core infrastructure, API client, and database connection layers have been established by Devansh.
""")

render_section_header("Module Responsibilities & Requirements", "Extracted from Project Guide (PDF Pages 4-5)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Database Schemas
    - **`complexes` Table:** `complex_id` (PK), `complex_name` (NOT NULL).
    - **`venues` Table:** `venue_id` (PK), `venue_name`, `city_name`, `country_name`, `country_code` (CHAR(3)), `timezone`, `complex_id` (FK).
    
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
    #### Deliverables Checklist for Module Owner
    - [ ] `sql/migrations/002_venues.sql`
    - [ ] `src/courtiq/domains/venues/extractor.py`
    - [ ] `src/courtiq/domains/venues/transformer.py`
    - [ ] `src/courtiq/domains/venues/repository.py`
    - [ ] `src/courtiq/domains/venues/analytics.py`
    - [ ] `sql/queries/venues/` (7 SQL query files)
    - [ ] Interactive UI on this page (`pages/2_Venues.py`)
    - [ ] Unit & Integration Tests in `tests/unit/venues/`
    - [ ] Subsequent Handoff Prompt: `docs/handoffs/RANKINGS_MODULE_HANDOFF.md`
    """)

st.markdown("---")
st.markdown("👉 **Please consult the comprehensive handoff guide:** `docs/handoffs/VENUES_MODULE_HANDOFF.md`")
