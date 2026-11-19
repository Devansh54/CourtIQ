
"""CourtIQ: Complexes & Venues Explorer.

Domain Contributor: Mansi (25% Workload Allocation)
Interactive Streamlit dashboard for tennis complexes and venues.
"""

import sys
from pathlib import Path

# Add src to Python path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

import pandas as pd
import streamlit as st

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

st.caption("Module Owner: Mansi | Venues & Complexes | 25% Contribution")

# ---------------------------------------------------------
# INITIALIZE REPOSITORY AND ANALYTICS
# ---------------------------------------------------------
@st.cache_resource
def get_venues_services():
    return VenuesRepository(), VenuesAnalytics()


try:
    repo, analytics = get_venues_services()

    # Load datasets
    venues_df = repo.query_1_venues_with_complex()
    complexes_df = repo.query_2_venues_count_per_complex()
    country_df = repo.query_6_venues_by_country_group()
    timezone_df = repo.query_4_venues_and_timezones()

except Exception as exc:
    st.error(f"Unable to load Venues data: {exc}")
    st.info(
        "Please verify PostgreSQL is running and database migrations "
        "have been applied."
    )
    st.stop()

# ---------------------------------------------------------
# SIDEBAR
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
            result = IngestionRunner().ingest_venues()

            if result.status == "SUCCESS":
                st.sidebar.success(result.message)
                st.rerun()
            else:
                st.sidebar.error(result.message)

        except Exception as exc:
            st.sidebar.error(f"Ingestion failed: {exc}")

st.sidebar.caption("Current data mode is configured in your .env file.")

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
    st.subheader("🏟️ Venues per Complex")

    try:
        complex_chart = analytics.create_complex_bar_chart()
        st.plotly_chart(complex_chart, use_container_width=True)
    except Exception as exc:
        st.warning(f"Complex chart unavailable: {exc}")

st.subheader("🕒 Timezone Distribution")

try:
    timezone_chart = analytics.create_timezone_pie_chart()
    st.plotly_chart(timezone_chart, use_container_width=True)
except Exception as exc:
    st.warning(f"Timezone chart unavailable: {exc}")

# ---------------------------------------------------------
# VENUES EXPLORER
# ---------------------------------------------------------
render_section_header(
    "🔎 Interactive Venues Explorer",
    "Search, filter and explore venue information.",
)

if not venues_df.empty:

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        countries = sorted(
            venues_df["country_name"].dropna().unique().tolist()
        )

        selected_country = st.selectbox(
            "Filter by Country",
            ["All Countries"] + countries,
        )

    with filter_col2:
        cities = sorted(
            venues_df["city_name"].dropna().unique().tolist()
        )

        selected_city = st.selectbox(
            "Filter by City",
            ["All Cities"] + cities,
        )

    search_text = st.text_input(
        "🔍 Search venue, complex or location",
        placeholder="Enter a venue, complex, city or country...",
    )

    filtered_df = venues_df.copy()

    if selected_country != "All Countries":
        filtered_df = filtered_df[
            filtered_df["country_name"] == selected_country
        ]

    if selected_city != "All Cities":
        filtered_df = filtered_df[
            filtered_df["city_name"] == selected_city
        ]

    if search_text.strip():
        mask = filtered_df.astype(str).apply(
            lambda column: column.str.contains(
                search_text.strip(),
                case=False,
                na=False,
            )
        ).any(axis=1)

        filtered_df = filtered_df[mask]

    st.metric("Matching Venues", len(filtered_df))

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Filtered Venues CSV",
        data=csv_data,
        file_name="courtiq_filtered_venues.csv",
        mime="text/csv",
    )

else:
    st.info("No venue records are currently available.")

# ---------------------------------------------------------
# COMPLEX EXPLORER
# ---------------------------------------------------------
render_section_header(
    "🏟️ Tennis Complex Explorer",
    "Explore complexes and the number of venues associated with each.",
)

if not complexes_df.empty:

    st.dataframe(
        complexes_df,
        use_container_width=True,
        hide_index=True,
    )

    complex_options = complexes_df["complex_name"].dropna().tolist()

    if complex_options:
        selected_complex = st.selectbox(
            "Select a Complex",
            complex_options,
        )

        selected_complex_venues = venues_df[
            venues_df["complex_name"] == selected_complex
        ]

        st.markdown(f"**Venues in {selected_complex}**")

        st.dataframe(
            selected_complex_venues,
            use_container_width=True,
            hide_index=True,
        )

else:
    st.info("No complex records are currently available.")

# ---------------------------------------------------------
# ADVANCED SQL QUERY EXPLORER
# ---------------------------------------------------------
render_section_header(
    "🧠 Advanced SQL Query Explorer",
    "Run all seven analytical queries implemented in the Venues module.",
)

query_options = {
    "Q1 - Venues with Complex Names": "q1",
    "Q2 - Venues Count per Complex": "q2",
    "Q3 - Venues by Country": "q3",
    "Q4 - Venues and Timezones": "q4",
    "Q5 - Complexes with Multiple Venues": "q5",
    "Q6 - Venues Grouped by Country": "q6",
    "Q7 - Venues for Specific Complex": "q7",
}

selected_query = st.selectbox(
    "Select Analytical Query",
    list(query_options.keys()),
)

query_result = pd.DataFrame()

try:
    if selected_query.startswith("Q1"):
        query_result = repo.query_1_venues_with_complex()

    elif selected_query.startswith("Q2"):
        query_result = repo.query_2_venues_count_per_complex()

    elif selected_query.startswith("Q3"):
        country_input = st.text_input(
            "Enter Country Name",
            value="Chile",
        )
        if country_input.strip():
            query_result = repo.query_3_venues_by_country(
                country_input.strip()
            )

    elif selected_query.startswith("Q4"):
        query_result = repo.query_4_venues_and_timezones()

    elif selected_query.startswith("Q5"):
        query_result = repo.query_5_multi_venue_complexes()

    elif selected_query.startswith("Q6"):
        query_result = repo.query_6_venues_by_country_group()

    elif selected_query.startswith("Q7"):
        complex_input = st.text_input(
            "Enter Complex Name",
            value="Nacional",
        )
        if complex_input.strip():
            query_result = repo.query_7_venues_for_specific_complex(
                complex_input.strip()
            )

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
        <p>Designed and implemented by Mansi | 25% Module Contribution</p>
        <p>Powered by Streamlit, PostgreSQL, Plotly and Sportradar data.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
