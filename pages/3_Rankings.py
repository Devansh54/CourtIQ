"""CourtIQ: Doubles Competitor Rankings Explorer.

Domain Contributor: Nilakshi (25% Workload Allocation)
Interactive Streamlit dashboard for doubles competitor standings, analytics, and SQL exploration.
"""

import sys
from pathlib import Path

# Add src to Python path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

import pandas as pd
import streamlit as st

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

st.caption("Module Owner: Nilakshi | Doubles Competitor Rankings | 25% Contribution")

# ---------------------------------------------------------
# INITIALIZE REPOSITORY AND ANALYTICS
# ---------------------------------------------------------
@st.cache_resource
def get_rankings_services():
    return RankingsRepository(), RankingsAnalytics()


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
    st.info(
        "Please verify PostgreSQL is running and database migrations "
        "have been applied."
    )
    st.stop()

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
            result = IngestionRunner().ingest_rankings()

            if result.status == "SUCCESS":
                st.sidebar.success(result.message)
                st.rerun()
            else:
                st.sidebar.error(result.message)

        except Exception as exc:
            st.sidebar.error(f"Ingestion failed: {exc}")

st.sidebar.caption("Current data mode is configured in your .env file.")

# ---------------------------------------------------------
# KPI METRICS OVERVIEW
# ---------------------------------------------------------
render_section_header(
    "📊 Doubles Rankings Intelligence Overview",
    "Live summary metrics calculated from the PostgreSQL database.",
)

try:
    kpis = analytics.get_summary_kpis()

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        render_metric_card(
            "Ranked Players",
            f"{kpis['total_competitors']:,}",
            "Competitors tracked",
        )

    with k2:
        render_metric_card(
            "Countries",
            f"{kpis['total_countries']:,}",
            "National federations",
        )

    with k3:
        render_metric_card(
            "Average Points",
            f"{kpis['average_points']:,.1f}",
            "Global point average",
        )

    with k4:
        render_metric_card(
            "World #1 Doubles",
            kpis["top_ranked_competitor"],
            "Official world rank 1",
        )

    with k5:
        render_metric_card(
            "Top Rank Gainer",
            kpis["biggest_rank_gainer"],
            "Weekly rank gain",
        )

except Exception as exc:
    st.warning(f"Could not calculate summary KPIs: {exc}")

# ---------------------------------------------------------
# DASHBOARD TABS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🏅 Leaderboard & Visualizations",
    "🌍 Country Analysis",
    "🔎 Interactive Filters & Search",
    "🧠 Advanced SQL Query Explorer",
])

# ---------------------------------------------------------
# TAB 1: LEADERBOARD & VISUALIZATIONS
# ---------------------------------------------------------
with tab1:
    render_section_header("Top Ranked Competitors", "Official world doubles standings")

    if not leaderboard.empty:
        st.dataframe(
            leaderboard,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No ranking records available. Ingest ranking data using the sidebar.")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("📊 Top Competitors by Points")
        try:
            fig_top = analytics.create_top_competitors_chart(limit=10)
            st.plotly_chart(fig_top, use_container_width=True)
        except Exception as exc:
            st.warning(f"Chart unavailable: {exc}")

    with chart_col2:
        st.subheader("📈 Competitions Played vs Points")
        try:
            fig_scatter = analytics.create_competitions_vs_points_scatter()
            st.plotly_chart(fig_scatter, use_container_width=True)
        except Exception as exc:
            st.warning(f"Chart unavailable: {exc}")

# ---------------------------------------------------------
# TAB 2: COUNTRY ANALYSIS
# ---------------------------------------------------------
with tab2:
    render_section_header(
        "Country Dominance & Point Distribution",
        "Competitor representation and cumulative point tallies by country",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌍 Competitors per Country")
        try:
            fig_country_bar = analytics.create_country_competitors_bar()
            st.plotly_chart(fig_country_bar, use_container_width=True)
        except Exception as exc:
            st.warning(f"Chart unavailable: {exc}")

    with col2:
        st.subheader("🍩 Points Share by Country")
        try:
            fig_points_pie = analytics.create_country_points_pie()
            st.plotly_chart(fig_points_pie, use_container_width=True)
        except Exception as exc:
            st.warning(f"Chart unavailable: {exc}")

    st.subheader("Country Standings Breakdown")
    if not points_by_country.empty:
        st.dataframe(
            points_by_country,
            use_container_width=True,
            hide_index=True,
        )

# ---------------------------------------------------------
# TAB 3: FILTERS & MOVEMENT
# ---------------------------------------------------------
with tab3:
    render_section_header(
        "Interactive Ranking Filters",
        "Explore competitors by country, name search, and ranking movement",
    )

    if not leaderboard.empty:
        countries = sorted(
            leaderboard["country"].dropna().unique().tolist()
        )

        filter_col1, filter_col2 = st.columns(2)

        with filter_col1:
            selected_country = st.selectbox(
                "Filter by Country",
                ["All Countries"] + countries,
            )

        with filter_col2:
            search_name = st.text_input("🔍 Search Competitor Name")

        filtered_data = leaderboard.copy()

        if selected_country != "All Countries":
            filtered_data = filtered_data[
                filtered_data["country"] == selected_country
            ]

        if search_name.strip():
            filtered_data = filtered_data[
                filtered_data["name"].str.contains(
                    search_name.strip(),
                    case=False,
                    na=False,
                )
            ]

        st.metric("Matching Competitors", len(filtered_data))

        st.dataframe(
            filtered_data,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = filtered_data.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Filtered Rankings CSV",
            data=csv_data,
            file_name="courtiq_filtered_rankings.csv",
            mime="text/csv",
        )

    st.subheader("🚀 Weekly Rank Gainers (Positive Movement)")
    if not gainers.empty:
        st.dataframe(
            gainers,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No competitors with positive weekly rank movement.")

    st.subheader("⚖️ Stable Ranking Competitors (Zero Movement)")
    if not stable_players.empty:
        st.dataframe(
            stable_players,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No competitors with stable ranking movement found.")

# ---------------------------------------------------------
# TAB 4: SQL QUERY CENTER
# ---------------------------------------------------------
with tab4:
    render_section_header(
        "Advanced SQL Query Explorer",
        "Execute and inspect all six analytical SQL queries implemented for the Rankings domain.",
    )

    query_options = {
        "Q1 - Top 10 Ranked Competitors": "q1",
        "Q2 - Rankings by Specific Country": "q2",
        "Q3 - Rank Movement Gainers": "q3",
        "Q4 - Competitions Played vs Points": "q4",
        "Q5 - Stable / Zero Movement Competitors": "q5",
        "Q6 - Points Distribution by Country": "q6",
    }

    selected_query_label = st.selectbox(
        "Select Analytical Query",
        list(query_options.keys()),
    )

    query_key = query_options[selected_query_label]
    query_result = pd.DataFrame()

    try:
        if query_key == "q1":
            query_result = repository.query_1_top_ranked_competitors()

        elif query_key == "q2":
            country_input = st.text_input(
                "Enter Country Name",
                value="Croatia",
            )
            if country_input.strip():
                query_result = repository.query_2_rankings_by_country(
                    country_input.strip()
                )

        elif query_key == "q3":
            query_result = repository.query_3_rank_movement_gainers()

        elif query_key == "q4":
            query_result = repository.query_4_competitions_played_vs_points()

        elif query_key == "q5":
            query_result = repository.query_5_unranked_or_zero_movement()

        elif query_key == "q6":
            query_result = repository.query_6_points_distribution_by_country()

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
        <p>Designed and implemented by Nilakshi | 25% Module Contribution</p>
        <p>Powered by Streamlit, PostgreSQL, Plotly and Sportradar data.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
