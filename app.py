"""CourtIQ: Tennis Data & Analytics Explorer.

Main Streamlit Application Shell & Homepage Dashboard.
Author: Devansh (Lead Architect & Core Contributor)
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
# Top Header Banner
# ------------------------------------------------------------------------------
st.markdown("""
<div class="courtiq-header-banner">
    <h1>🎾 CourtIQ</h1>
    <p>Tennis Data & Analytics Explorer — Explore Competitions. Analyse Rankings. Discover Tennis.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# Global Dashboard KPIs
# ------------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

total_competitions = repo.get_competition_count()
total_categories = repo.get_category_count()

# Check venues & competitors if tables exist
venues_count = 0
competitors_count = 0
try:
    v_row = db.fetch_one("SELECT COUNT(*) AS count FROM venues;")
    if v_row:
        venues_count = v_row["count"]
except Exception:
    venues_count = 0

try:
    c_row = db.fetch_one("SELECT COUNT(*) AS count FROM competitors;")
    if c_row:
        competitors_count = c_row["count"]
except Exception:
    competitors_count = 0

with col1:
    render_metric_card("Total Competitions", f"{total_competitions:,}", "Tournaments & Events")
with col2:
    render_metric_card("Governing Categories", f"{total_categories:,}", "ATP, WTA, ITF, Grand Slam")
with col3:
    venue_sub = "Venues & Stadia" if venues_count > 0 else "Pending Venue Owner (25%)"
    render_metric_card("Sports Venues", f"{venues_count:,}" if venues_count > 0 else "—", venue_sub)
with col4:
    comp_sub = "Ranked Players" if competitors_count > 0 else "Pending Rankings Owner (25%)"
    render_metric_card("Doubles Competitors", f"{competitors_count:,}" if competitors_count > 0 else "—", comp_sub)

# ------------------------------------------------------------------------------
# Ingestion Status & Quick Controls
# ------------------------------------------------------------------------------
if total_competitions == 0:
    st.warning("⚠️ Database is currently unpopulated. Click the button below to ingest competition data.")
    if st.button("🚀 Ingest Competitions & Categories Data", type="primary"):
        with st.spinner("Executing database migrations and ingesting competitions..."):
            runner = IngestionRunner(db)
            res = runner.ingest_competitions()
            if res.status == "SUCCESS":
                st.success(f"Ingestion successful! {res.categories_ingested} categories and {res.competitions_ingested} competitions loaded.")
                st.rerun()
            else:
                st.error(f"Ingestion failed: {res.message}")

# ------------------------------------------------------------------------------
# Domain Modules Explorer
# ------------------------------------------------------------------------------
render_section_header("Platform Modules & Team Contribution Architecture", "Sequential group engineering roadmap (50% / 25% / 25%)")

m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    st.markdown("""
    ### 🏆 1. Competitions & Categories
    **Owner:** Devansh (50% Milestone)  
    **Status:** `ACTIVE / FULLY IMPLEMENTED`  
    
    Explore tournament hierarchies, Grand Slams, ATP/WTA/ITF circuits, formats, and all 7 analytical queries.
    """)
    st.page_link("pages/1_Competitions.py", label="Open Competitions Explorer ➜", icon="🏆")

with m_col2:
    st.markdown("""
    ### 🏟️ 2. Complexes & Venues
    **Owner:** Venue & Complexes Module Owner (25%)  
    **Status:** `READY FOR IMPLEMENTATION`  
    
    Geographic mapping of global sports complexes, arenas, timezones, and venue infrastructure.
    """)
    st.page_link("pages/2_Venues.py", label="Open Venues Module ➜", icon="🏟️")

with m_col3:
    st.markdown("""
    ### 🥇 3. Doubles Competitor Rankings
    **Owner:** Rankings & Analytics Module Owner (25%)  
    **Status:** `READY FOR IMPLEMENTATION`  
    
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
    st.markdown("#### Team Workload Allocation")
    st.markdown("- **Devansh (50%):** Overall Architecture, Core Infra, Competitions Domain")
    st.markdown("- **Venue & Complexes Module Owner (25%):** Complexes, Venues & Related Analytics")
    st.markdown("- **Rankings & Analytics Module Owner (25%):** Doubles Competitor Rankings & Integration")
    st.markdown("- **Single Source of Truth:** `docs/TEAM_WORK_ALLOCATION.md`")
