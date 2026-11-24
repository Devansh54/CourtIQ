"""CourtIQ: Tennis Data & Analytics Explorer.

Main Streamlit Application Shell & Homepage Dashboard.
"""

import sys
from pathlib import Path

# Ensure src is in Python path
_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT / "src"))

import streamlit as st
from courtiq.core.config import get_settings
from courtiq.core.database import get_db
from courtiq.domains.competitions.repository import CompetitionsRepository
from courtiq.ingestion.runner import IngestionRunner
from courtiq.utils.formatting import apply_custom_css, render_metric_card, render_section_header

# ------------------------------------------------------------------------------
# Streamlit App Configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="CourtIQ – Tennis Data & Analytics Explorer",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()
settings = get_settings()
db = get_db()
repo = CompetitionsRepository(db)

# ------------------------------------------------------------------------------
# Sidebar Global Controls
# ------------------------------------------------------------------------------
st.sidebar.title("🎾 CourtIQ Platform")
if st.sidebar.button("🔄 Refresh Application", use_container_width=True):
    st.cache_resource.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Data Actions")
if st.sidebar.button("⚡ Initialize & Seed All Data", use_container_width=True):
    with st.spinner("Applying migrations and ingesting all demo data..."):
        try:
            runner = IngestionRunner(db)
            runner.run_migrations_if_needed()
            runner.ingest_competitions()
            runner.ingest_venues()
            runner.ingest_rankings()
            st.sidebar.success("All domains initialized and seeded successfully!")
            st.cache_resource.clear()
            st.rerun()
        except Exception as exc:
            st.sidebar.error(f"Initialization failed: {exc}")

st.sidebar.caption("Mode: " + settings.courtiq_mode)

# ------------------------------------------------------------------------------
# Top Header Banner
# ------------------------------------------------------------------------------
st.markdown("""
<div class="courtiq-header-banner">
    <h1>🎾 CourtIQ</h1>
    <p>Tennis Data & Analytics Explorer — Explore Competitions. Analyse Rankings. Discover Tennis.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# Global Dashboard KPIs (Safe Checks)
# ------------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

total_competitions = 0
total_categories = 0
venues_count = 0
competitors_count = 0

try:
    if db.table_exists("competitions"):
        total_competitions = repo.get_competition_count()
    if db.table_exists("categories"):
        total_categories = repo.get_category_count()
except Exception:
    total_competitions = 0
    total_categories = 0

try:
    if db.table_exists("venues"):
        v_row = db.fetch_one("SELECT COUNT(*) AS count FROM venues;")
        if v_row:
            venues_count = v_row["count"]
except Exception:
    venues_count = 0

try:
    if db.table_exists("competitors"):
        c_row = db.fetch_one("SELECT COUNT(*) AS count FROM competitors;")
        if c_row:
            competitors_count = c_row["count"]
except Exception:
    competitors_count = 0

with col1:
    render_metric_card("Total Competitions", f"{total_competitions:,}" if total_competitions > 0 else "—", "Tournaments & Events" if total_competitions > 0 else "Ready / Ingest Data")
with col2:
    render_metric_card("Governing Categories", f"{total_categories:,}" if total_categories > 0 else "—", "ATP, WTA, ITF, Grand Slam" if total_categories > 0 else "Ready / Ingest Data")
with col3:
    venue_sub = "Venues & Stadia" if venues_count > 0 else "Ready / Ingest Data"
    render_metric_card("Sports Venues", f"{venues_count:,}" if venues_count > 0 else "—", venue_sub)
with col4:
    comp_sub = "Ranked Players" if competitors_count > 0 else "Ready / Ingest Data"
    render_metric_card("Doubles Competitors", f"{competitors_count:,}" if competitors_count > 0 else "—", comp_sub)

# ------------------------------------------------------------------------------
# Ingestion Status & 1-Click Platform Setup
# ------------------------------------------------------------------------------
needs_init = (total_competitions == 0 or venues_count == 0 or competitors_count == 0)
if needs_init:
    st.info("💡 **Quick Start:** Some database domains have not been populated yet. Click below to run migrations and populate all demo data with one click.")
    if st.button("⚡ Initialize Entire Platform & Ingest All Demo Data", type="primary", use_container_width=True):
        with st.spinner("Applying database migrations and seeding demo data across all domains..."):
            runner = IngestionRunner(db)
            runner.run_migrations_if_needed()
            if total_competitions == 0:
                runner.ingest_competitions()
            if venues_count == 0:
                runner.ingest_venues()
            if competitors_count == 0:
                runner.ingest_rankings()
            st.success("All platform domains initialized and demo data ingested successfully!")
            st.cache_resource.clear()
            st.rerun()

# ------------------------------------------------------------------------------
# Domain Modules Explorer
# ------------------------------------------------------------------------------
render_section_header("Platform Modules & Domain Architecture", "Explore structured tennis analytics across all three core platform domains")

m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    st.markdown("""
    ### 🏆 1. Competitions & Categories
    **Domain:** Tournament Structures & Hierarchies  
    **Status:** `ACTIVE / FULLY IMPLEMENTED`  
    
    Explore tournament hierarchies, Grand Slams, ATP/WTA/ITF circuits, formats, and all 7 analytical queries.
    """)
    st.page_link("pages/1_Competitions.py", label="Open Competitions Explorer ➜", icon="🏆")

with m_col2:
    st.markdown("""
    ### 🏟️ 2. Complexes & Venues
    **Domain:** Tennis Complexes, Stadiums & Geo Analytics  
    **Status:** `ACTIVE / FULLY IMPLEMENTED`  
    
    Geographic mapping of global sports complexes, arenas, timezones, and venue infrastructure.
    """)
    st.page_link("pages/2_Venues.py", label="Open Venues Module ➜", icon="🏟️")

with m_col3:
    st.markdown("""
    ### 🥇 3. Doubles Competitor Rankings
    **Domain:** World Doubles Standings & Performance Trends  
    **Status:** `ACTIVE / FULLY IMPLEMENTED`  
    
    Weekly world doubles standings, movement metrics, country dominance, and player profiles.
    """)
    st.page_link("pages/3_Rankings.py", label="Open Rankings Module ➜", icon="🥇")

# ------------------------------------------------------------------------------
# Architectural Overview & Environment Info
# ------------------------------------------------------------------------------
render_section_header("Technical Architecture & System Telemetry")

env_col1, env_col2 = st.columns(2)

with env_col1:
    st.markdown("#### Runtime Configuration")
    mode_text = "Synthetic Mock / Demo Mode" if settings.is_demo_mode else "Sportradar Live API Mode"
    db_target = "PostgreSQL 18 (Primary Production Engine)" if settings.is_postgres else "SQLite (Fallback / Local Testing)"
    st.markdown(f"- **Operating Mode:** `{settings.courtiq_mode}` ({mode_text})")
    st.markdown(f"- **Relational Database:** `{db_target}`")
    st.markdown(f"- **Database Dialect:** `{settings.db_dialect}`")
    if settings.is_postgres:
        st.markdown(f"- **Pool Configuration:** `size={settings.db_pool_size}, max_overflow={settings.db_pool_max_overflow}, timeout={settings.db_pool_timeout}s`")
    else:
        st.markdown(f"- **Database Path:** `{settings.courtiq_db_path}`")
    st.markdown(f"- **API Base Endpoint:** `{settings.sportradar_base_url}`")
    st.markdown(f"- **Rate Limit Safety:** `{settings.sportradar_rate_limit_rps} RPS`")

with env_col2:
    st.markdown("#### Platform Capabilities")
    st.markdown("- **Competitions & Categories:** 7 Parameterized SQL Queries & Interactive Hierarchy Explorer")
    st.markdown("- **Complexes & Venues:** 7 Infrastructure & Geographic Queries with Court Distribution Visualizations")
    st.markdown("- **Doubles Rankings:** 6 Leaderboard & Movement Queries, Country Dominance Analysis")
    st.markdown("- **Database Integrity:** PostgreSQL 18 with Connection Pooling & Alembic DDL Versioning")
