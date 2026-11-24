"""CourtIQ: Complexes & Venues Explorer.

Interactive Streamlit dashboard for tennis complexes and venues.
"""

import sys
from pathlib import Path

# Add src to Python path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

import pandas as pd
import streamlit as st

from courtiq.core.database import get_db
from courtiq.domains.venues.analytics import VenuesAnalytics
from courtiq.domains.venues.repository import VenuesRepository
from courtiq.ingestion.runner import IngestionRunner
from courtiq.utils.formatting import (
    apply_custom_css,
    render_metric_card,
    render_section_header,
)

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Venues Explorer | CourtIQ",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()
db = get_db()

# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.title("🎾 Venues Controls")

if st.sidebar.button("🔄 Refresh Dashboard", use_container_width=True):
    st.cache_resource.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Data Management")

if st.sidebar.button("⬇️ Run Venues Ingestion", use_container_width=True):
    with st.spinner("Extracting and saving Venues data..."):
        try:
            result = IngestionRunner(db).ingest_venues()
            if result.status == "SUCCESS":
                st.sidebar.success(result.message)
                st.cache_resource.clear()
                st.rerun()
            else:
                st.sidebar.error(result.message)
        except Exception as exc:
            st.sidebar.error(f"Ingestion failed: {exc}")

st.sidebar.caption("Current data mode is configured in your .env file.")

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown(
    """
    <div class="courtiq-header-banner">
        <h1>🎾 CourtIQ | Venues Intelligence</h1>
        <p>
            Explore Tennis Complexes, Stadiums, Geographic Distribution
            and Timezone Analytics.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Explore Tennis Complexes, Stadiums, Geographic Distribution and Timezone Analytics.")

# ---------------------------------------------------------
# DATABASE INITIALIZATION & EMPTY STATE CHECKS
# ---------------------------------------------------------
tables_exist = False
try:
    tables_exist = db.table_exists("venues") and db.table_exists("complexes")
except Exception:
    tables_exist = False

if not tables_exist:
    st.warning("⚠️ **Venues database tables are not initialized yet.**")
    st.markdown("The database schema for `complexes` and `venues` has not been applied.")
    if st.button("🚀 Initialize Database & Ingest Demo Data", type="primary", use_container_width=True):
        with st.spinner("Applying database migrations and ingesting data..."):
            res = IngestionRunner(db).ingest_venues()
            if res.status == "SUCCESS":
                st.success("Venues initialized successfully!")
                st.cache_resource.clear()
                st.rerun()
            else:
                st.error(f"Initialization failed: {res.message}")
    st.stop()

# Check row count
venues_count = 0
try:
    v_row = db.fetch_one("SELECT COUNT(*) AS count FROM venues;")
    venues_count = v_row["count"] if v_row else 0
except Exception:
    venues_count = 0

if venues_count == 0:
    st.info("ℹ️ **Venues database is currently empty.**")
    st.markdown("Database tables exist, but no venues or complexes have been ingested yet.")
    if st.button("📥 Ingest Venues Demo Data Now", type="primary", use_container_width=True):
        with st.spinner("Ingesting venues demo data..."):
            res = IngestionRunner(db).ingest_venues()
            if res.status == "SUCCESS":
                st.success("Venues data ingested successfully!")
                st.cache_resource.clear()
                st.rerun()
            else:
                st.error(f"Ingestion failed: {res.message}")
    st.stop()

# ---------------------------------------------------------
# INITIALIZE REPOSITORY AND ANALYTICS
# ---------------------------------------------------------
@st.cache_resource
def get_venues_services():
    return VenuesRepository(db), VenuesAnalytics(VenuesRepository(db))


try:
    repo, analytics = get_venues_services()

    # Load datasets
    venues_df = repo.query_1_venues_with_complex()
    complexes_df = repo.query_2_venues_count_per_complex()
    country_df = repo.query_6_venues_by_country_group()
    timezone_df = repo.query_4_venues_and_timezones()

except Exception as exc:
    st.error(f"Unable to load Venues data: {exc}")
    st.stop()

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
render_section_header(
    "📊 Venues Intelligence Overview",
    "Live summary calculated from the PostgreSQL database.",
)

try:
    kpis = analytics.get_summary_kpis()

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        render_metric_card(
            "Total Complexes",
            f"{kpis['total_complexes']:,}",
            "Tennis infrastructure",
        )

    with k2:
        render_metric_card(
            "Total Venues",
            f"{kpis['total_venues']:,}",
            "Registered venues",
        )

    with k3:
        render_metric_card(
            "Countries",
            f"{kpis['total_countries']:,}",
            "Global coverage",
        )

    with k4:
        render_metric_card(
            "Cities",
            f"{kpis['total_cities']:,}",
            "Unique locations",
        )

    with k5:
        render_metric_card(
            "Avg Venues / Complex",
            f"{kpis['average_venues_per_complex']:.2f}",
            "Infrastructure density",
        )

except Exception as exc:
    st.warning(f"Could not calculate summary KPIs: {exc}")

# ---------------------------------------------------------
# ANALYTICS CHARTS
# ---------------------------------------------------------
render_section_header(
    "📈 Geographic & Infrastructure Analytics",
    "Visual insights into country distribution, complexes and timezones.",
)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("🌍 Venues by Country")

    try:
        country_chart = analytics.create_country_bar_chart()
        st.plotly_chart(country_chart, use_container_width=True)
    except Exception as exc:
        st.warning(f"Country chart unavailable: {exc}")

with chart_col2:
    st.subheader("🕒 Timezone Coverage")

    try:
        timezone_chart = analytics.create_timezone_pie_chart()
        st.plotly_chart(timezone_chart, use_container_width=True)
    except Exception as exc:
        st.warning(f"Timezone chart unavailable: {exc}")

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏟️ All Venues",
        "🏢 Complexes & Capacity",
        "🔍 Filter & Search",
        "⚡ SQL Query Explorer",
    ]
)

with tab1:
    st.subheader("Registered Tennis Venues")

    if not venues_df.empty:
        st.dataframe(
            venues_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No venue records available.")

with tab2:
    st.subheader("Complexes & Venue Density")

    if not complexes_df.empty:
        st.dataframe(
            complexes_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No complex records available.")

    st.markdown("---")
    st.subheader("Multi-Venue Sports Complexes")

    try:
        multi_venues_df = repo.query_5_multi_venue_complexes()

        if not multi_venues_df.empty:
            st.dataframe(
                multi_venues_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No multi-venue complexes found.")

    except Exception as exc:
        st.warning(f"Unable to load multi-venue complexes: {exc}")

with tab3:
    st.subheader("Interactive Venue Search")

    search_col1, search_col2 = st.columns(2)

    with search_col1:
        country_options = ["All"] + sorted(
            [c for c in venues_df["country_name"].dropna().unique()]
        )
        selected_country = st.selectbox(
            "Filter by Country:",
            country_options,
        )

    with search_col2:
        search_term = st.text_input(
            "Search Venue or City Name:",
            placeholder="e.g. Center Court, Paris, London...",
        )

    filtered_df = venues_df.copy()

    if selected_country != "All":
        filtered_df = filtered_df[
            filtered_df["country_name"] == selected_country
        ]

    if search_term.strip():
        term = search_term.strip().lower()
        filtered_df = filtered_df[
            filtered_df["venue_name"].str.lower().str.contains(term, na=False)
            | filtered_df["city_name"].str.lower().str.contains(term, na=False)
        ]

    st.markdown(f"**Found {len(filtered_df)} matching venues:**")
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
    )

with tab4:
    st.subheader("⚡ Required SQL Queries Explorer")

    queries_map = {
        "Q1: Venues with Associated Complex": (
            "q1_venues_with_complex.sql",
            lambda: repo.query_1_venues_with_complex(),
        ),
        "Q2: Venues Count per Complex": (
            "q2_venues_count_per_complex.sql",
            lambda: repo.query_2_venues_count_per_complex(),
        ),
        "Q3: Venues by Country": (
            "q3_venues_by_country.sql",
            lambda: repo.query_3_venues_by_country(),
        ),
        "Q4: Venues and Timezones": (
            "q4_venues_and_timezones.sql",
            lambda: repo.query_4_venues_and_timezones(),
        ),
        "Q5: Multi-Venue Complexes": (
            "q5_multi_venue_complexes.sql",
            lambda: repo.query_5_multi_venue_complexes(),
        ),
        "Q6: Venues by Country Group": (
            "q6_venues_by_country_group.sql",
            lambda: repo.query_6_venues_by_country_group(),
        ),
        "Q7: Venues for Specific Complex (Search)": (
            "q7_venues_for_specific_complex.sql",
            None,
        ),
    }

    selected_query_label = st.selectbox(
        "Select Analytical Query to Inspect and Execute:",
        list(queries_map.keys()),
    )

    sql_file, executor = queries_map[selected_query_label]

    try:
        sql_content = repo._read_query(sql_file)
        st.markdown("#### SQL Statement:")
        st.code(sql_content, language="sql")

        if selected_query_label.startswith("Q7"):
            complex_term = st.text_input(
                "Enter Complex Name Pattern:",
                value="Nacional",
            )
            query_result = repo.query_7_venues_for_specific_complex(
                complex_term
            )
        else:
            query_result = executor()

        st.markdown("#### Execution Results:")
        st.dataframe(
            query_result,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(f"Query returned {len(query_result)} records.")

    except Exception as exc:
        st.error(f"Unable to execute selected query: {exc}")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; padding: 1rem;">
        <h4>🎾 CourtIQ | Venues Intelligence Module</h4>
        <p>CourtIQ Tennis Analytics Platform — Venues & Infrastructure</p>
        <p>Powered by Streamlit, PostgreSQL, Plotly and Sportradar data.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
