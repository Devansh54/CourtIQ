"""CourtIQ: Doubles Competitor Rankings Explorer.

Interactive Streamlit dashboard for doubles competitor standings, analytics, and SQL exploration.
"""

import sys
from pathlib import Path

# Add src to Python path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

import pandas as pd
import streamlit as st

from courtiq.core.database import get_db
from courtiq.domains.rankings.analytics import RankingsAnalytics
from courtiq.domains.rankings.repository import RankingsRepository
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
    page_title="Rankings Explorer | CourtIQ",
    page_icon="🥇",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()
db = get_db()
if not hasattr(db, "table_exists"):
    import importlib
    import courtiq.core.database as db_mod
    importlib.reload(db_mod)
    db = db_mod.get_db()

# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.title("🥇 Rankings Controls")

if st.sidebar.button("🔄 Refresh Dashboard", use_container_width=True):
    st.cache_resource.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Data Management")

if st.sidebar.button("⬇️ Run Rankings Ingestion", use_container_width=True):
    with st.spinner("Extracting and saving Rankings data..."):
        try:
            result = IngestionRunner(db).ingest_rankings()
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
        <h1>🥇 CourtIQ | Doubles Rankings Intelligence</h1>
        <p>
            Explore World Doubles Standings, Point Tallies, Week-over-Week Movement,
            and Country Dominance.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Explore World Doubles Standings, Point Tallies, Week-over-Week Movement, and Country Dominance.")

# ---------------------------------------------------------
# DATABASE INITIALIZATION & EMPTY STATE CHECKS
# ---------------------------------------------------------
tables_exist = False
try:
    tables_exist = db.table_exists("competitor_rankings") and db.table_exists("competitors")
except Exception:
    tables_exist = False

if not tables_exist:
    st.warning("⚠️ **Rankings database tables are not initialized yet.**")
    st.markdown("The database schema for `competitors` and `competitor_rankings` has not been applied.")
    if st.button("🚀 Initialize Database & Ingest Demo Data", type="primary", use_container_width=True):
        with st.spinner("Applying database migrations and ingesting data..."):
            res = IngestionRunner(db).ingest_rankings()
            if res.status == "SUCCESS":
                st.success("Rankings initialized successfully!")
                st.cache_resource.clear()
                st.rerun()
            else:
                st.error(f"Initialization failed: {res.message}")
    st.stop()

# Check row count
rankings_count = 0
try:
    r_row = db.fetch_one("SELECT COUNT(*) AS count FROM competitor_rankings;")
    rankings_count = r_row["count"] if r_row else 0
except Exception:
    rankings_count = 0

if rankings_count == 0:
    st.info("ℹ️ **Rankings database is currently empty.**")
    st.markdown("Database tables exist, but no competitor rankings data has been ingested yet.")
    if st.button("📥 Ingest Rankings Demo Data Now", type="primary", use_container_width=True):
        with st.spinner("Ingesting rankings demo data..."):
            res = IngestionRunner(db).ingest_rankings()
            if res.status == "SUCCESS":
                st.success("Rankings data ingested successfully!")
                st.cache_resource.clear()
                st.rerun()
            else:
                st.error(f"Ingestion failed: {res.message}")
    st.stop()

# ---------------------------------------------------------
# INITIALIZE REPOSITORY AND ANALYTICS
# ---------------------------------------------------------
@st.cache_resource
def get_rankings_services():
    return RankingsRepository(db), RankingsAnalytics(RankingsRepository(db))


try:
    repository, analytics = get_rankings_services()

    # Load datasets
    leaderboard = repository.query_1_top_ranked_competitors()
    country_data = repository.query_5_competitors_per_country()
    points_by_country = repository.query_6_points_distribution_by_country()
    stable_players = repository.query_5_unranked_or_zero_movement()
    gainers = repository.query_3_rank_movement_gainers()

except Exception as exc:
    st.error(f"Unable to load Rankings data: {exc}")
    st.stop()

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
render_section_header(
    "📊 Global Doubles Rankings Overview",
    "Live competitor statistics calculated from the PostgreSQL database.",
)

try:
    kpis = analytics.get_summary_kpis()

    top_rank = kpis.get("top_rank", 1)
    top_name = kpis.get("top_competitor_name") or kpis.get("top_ranked_competitor", "N/A")
    total_ranked = kpis.get("total_ranked_players") or kpis.get("total_competitors", 0)
    avg_pts = float(kpis.get("average_points", 0.0))
    tot_countries = kpis.get("total_countries", 0)
    max_pts = kpis.get("max_points", 0)

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        render_metric_card(
            "Top Ranked Player",
            f"#{top_rank}",
            top_name,
        )

    with k2:
        render_metric_card(
            "Total Ranked Players",
            f"{total_ranked:,}",
            "Active Doubles",
        )

    with k3:
        render_metric_card(
            "Average Points",
            f"{avg_pts:,.1f}",
            "Points per Player",
        )

    with k4:
        render_metric_card(
            "Represented Countries",
            f"{tot_countries:,}",
            "Global Coverage",
        )

    with k5:
        render_metric_card(
            "Highest Point Total",
            f"{max_pts:,}",
            "World Leading Tally",
        )

except Exception as exc:
    st.warning(f"Could not calculate summary KPIs: {exc}")

# ---------------------------------------------------------
# ANALYTICS CHARTS
# ---------------------------------------------------------
render_section_header(
    "📈 Performance & Geographic Analytics",
    "Visual insights into rankings, point distributions, and country dominance.",
)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("🏆 Top Ranked Doubles Players")
    try:
        top_chart = analytics.create_top_competitors_chart(limit=10)
        st.plotly_chart(top_chart, use_container_width=True)
    except Exception as exc:
        st.warning(f"Top competitors chart unavailable: {exc}")

with chart_col2:
    st.subheader("🎾 Competitions Played vs. Points")
    try:
        scatter_chart = analytics.create_competitions_vs_points_scatter()
        st.plotly_chart(scatter_chart, use_container_width=True)
    except Exception as exc:
        st.warning(f"Competitions vs points chart unavailable: {exc}")

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.subheader("🌍 Points Distribution by Country")
    try:
        pie_chart = analytics.create_country_points_pie()
        st.plotly_chart(pie_chart, use_container_width=True)
    except Exception as exc:
        st.warning(f"Country points distribution chart unavailable: {exc}")

with chart_col4:
    st.subheader("👥 Competitors per Country")
    try:
        bar_chart = analytics.create_country_competitors_bar()
        st.plotly_chart(bar_chart, use_container_width=True)
    except Exception as exc:
        st.warning(f"Competitors per country chart unavailable: {exc}")

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏆 Leaderboard",
        "🌍 Geographic Distribution",
        "📈 Movement & Stability",
        "⚡ SQL Query Explorer",
    ]
)

with tab1:
    st.subheader("Official Doubles Rankings Leaderboard")

    if not leaderboard.empty:
        st.dataframe(
            leaderboard,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No leaderboard records available.")

with tab2:
    st.subheader("Country Representation & Point Totals")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Competitor Count by Country")
        if not country_data.empty:
            st.dataframe(
                country_data,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No country count data available.")

    with col_b:
        st.markdown("#### Total Ranking Points by Country")
        if not points_by_country.empty:
            st.dataframe(
                points_by_country,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No country points data available.")

with tab3:
    st.subheader("Weekly Movement & Zero-Movement Competitors")

    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("#### Rank Gainers (Positive Movement)")
        if not gainers.empty:
            st.dataframe(
                gainers,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No rank gainers found.")

    with col_d:
        st.markdown("#### Stable / Zero Movement Competitors")
        if not stable_players.empty:
            st.dataframe(
                stable_players,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No stable player records found.")

with tab4:
    st.subheader("⚡ Required SQL Queries Explorer")

    queries_map = {
        "Q1: Top Ranked Competitors": (
            "q1_top_ranked_competitors.sql",
            lambda: repository.query_1_top_ranked_competitors(),
        ),
        "Q2: Rankings by Country": (
            "q2_rankings_by_country.sql",
            lambda: repository.query_2_rankings_by_country(),
        ),
        "Q3: Rank Movement Gainers": (
            "q3_rank_movement_gainers.sql",
            lambda: repository.query_3_rank_movement_gainers(),
        ),
        "Q4: Competitions Played vs Points": (
            "q4_competitions_played_vs_points.sql",
            lambda: repository.query_4_competitions_played_vs_points(),
        ),
        "Q5: Unranked or Zero Movement Competitors": (
            "q5_unranked_or_zero_movement_competitors.sql",
            lambda: repository.query_5_unranked_or_zero_movement(),
        ),
        "Q6: Points Distribution by Country": (
            "q6_points_distribution_by_country.sql",
            lambda: repository.query_6_points_distribution_by_country(),
        ),
    }

    selected_query_label = st.selectbox(
        "Select Analytical Query to Inspect and Execute:",
        list(queries_map.keys()),
    )

    sql_file, executor = queries_map[selected_query_label]

    try:
        sql_content = repository._read_query(sql_file)
        st.markdown("#### SQL Statement:")
        st.code(sql_content, language="sql")

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
        <h4>🥇 CourtIQ | Doubles Rankings Intelligence Module</h4>
        <p>CourtIQ Tennis Analytics Platform — Competitor Rankings</p>
        <p>Powered by Streamlit, PostgreSQL, Plotly and Sportradar data.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
