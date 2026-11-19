"""CourtIQ: Doubles Competitor Rankings Explorer."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st
import plotly.express as px

from courtiq.utils.formatting import (
    apply_custom_css,
    render_section_header,
)
from courtiq.domains.rankings.repository import RankingsRepository


st.set_page_config(
    page_title="Rankings Explorer | CourtIQ",
    page_icon="🥇",
    layout="wide",
)

apply_custom_css()

st.title("🥇 Doubles Competitor Rankings Explorer")
st.caption("CourtIQ | Rankings & Analytics")

try:
    repository = RankingsRepository()

    # -------------------------------------------------
    # KPI SUMMARY
    # -------------------------------------------------

    summary = repository.db.fetch_one("""
        SELECT
            COUNT(DISTINCT c.competitor_id) AS total_competitors,
            COUNT(DISTINCT c.country_code) AS total_countries,
            ROUND(AVG(cr.points)::numeric, 2) AS average_points,
            (
                SELECT c2.name
                FROM competitor_rankings cr2
                JOIN competitors c2
                    ON cr2.competitor_id = c2.competitor_id
                ORDER BY cr2.rank ASC
                LIMIT 1
            ) AS top_player,
            (
                SELECT c3.name
                FROM competitor_rankings cr3
                JOIN competitors c3
                    ON cr3.competitor_id = c3.competitor_id
                WHERE cr3.movement > 0
                ORDER BY cr3.movement DESC, cr3.rank ASC
                LIMIT 1
            ) AS biggest_gainer
        FROM competitors c
        JOIN competitor_rankings cr
            ON c.competitor_id = cr.competitor_id
    """)

    summary = summary or {}

    total_competitors = summary.get("total_competitors") or 0
    total_countries = summary.get("total_countries") or 0
    average_points = summary.get("average_points") or 0
    top_player = summary.get("top_player") or "N/A"
    biggest_gainer = summary.get("biggest_gainer") or "N/A"

    render_section_header("Rankings Overview", "Current doubles competitor ranking statistics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Competitors", total_competitors)
    col2.metric("Countries Represented", total_countries)
    col3.metric("Average Points", average_points)
    col4.metric("Top Ranked Player", top_player)

    st.info(f"🏆 Biggest Rank Gainer: **{biggest_gainer}**")

    # -------------------------------------------------
    # LOAD ANALYTICAL DATA
    # -------------------------------------------------

    leaderboard = repository.query_1_competitors_rank_points()
    top_five = repository.query_2_top_5_competitors()
    stable_players = repository.query_3_stable_rank_competitors()
    country_data = repository.query_5_competitors_per_country()
    highest_points = repository.query_6_highest_points_competitors()
    points_by_country = repository._read_query(
        "q6_points_distribution_by_country.sql"
    )
    points_by_country = repository.db.fetch_df(points_by_country)
    scatter_data = repository.db.fetch_df(
        repository._read_query("q4_competitions_played_vs_points.sql")
    )

    # -------------------------------------------------
    # DASHBOARD TABS
    # -------------------------------------------------

    tab1, tab2, tab3, tab4 = st.tabs([
        "🏅 Leaderboard & Charts",
        "🌍 Country Analysis",
        "🔎 Filters",
        "📊 SQL Query Center",
    ])

    # -------------------------------------------------
    # TAB 1: LEADERBOARD AND CHARTS
    # -------------------------------------------------

    with tab1:
        render_section_header("Top Competitors", "Current ranking leaderboard")

        if not leaderboard.empty:
            st.dataframe(
                leaderboard,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No ranking records available.")

        st.markdown("### Top 10 Competitors by Points")

        if not highest_points.empty:
            fig = px.bar(
                highest_points.sort_values("points"),
                x="points",
                y="name",
                orientation="h",
                title="Competitor Points Comparison",
                labels={"points": "Points", "name": "Competitor"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No points data available.")

        st.markdown("### Competitions Played vs Points")

        if not scatter_data.empty:
            fig = px.scatter(
                scatter_data,
                x="competitions_played",
                y="points",
                hover_name="name",
                title="Competitions Played vs Points",
                labels={
                    "competitions_played": "Competitions Played",
                    "points": "Points",
                },
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No comparison data available.")

    # -------------------------------------------------
    # TAB 2: COUNTRY ANALYSIS
    # -------------------------------------------------

    with tab2:
        render_section_header(
            "Country Dominance",
            "Competitor representation and points by country",
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Competitors per Country")

            if not country_data.empty:
                fig = px.bar(
                    country_data,
                    x="country",
                    y="total_competitors",
                    title="Competitors by Country",
                    labels={
                        "country": "Country",
                        "total_competitors": "Competitors",
                    },
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Points Distribution by Country")

            if not points_by_country.empty:
                fig = px.pie(
                    points_by_country,
                    names="country",
                    values="total_points",
                    hole=0.4,
                    title="Total Points by Country",
                )
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Country Statistics")

        if not points_by_country.empty:
            st.dataframe(
                points_by_country,
                use_container_width=True,
                hide_index=True,
            )

    # -------------------------------------------------
    # TAB 3: FILTERS
    # -------------------------------------------------

    with tab3:
        render_section_header(
            "Ranking Filters",
            "Explore competitors by country and ranking movement",
        )

        if not leaderboard.empty:
            countries = sorted(
                leaderboard["country"].dropna().unique().tolist()
            )

            selected_country = st.selectbox(
                "Select Country",
                ["All Countries"] + countries,
            )

            filtered_data = leaderboard.copy()

            if selected_country != "All Countries":
                filtered_data = filtered_data[
                    filtered_data["country"] == selected_country
                ]

            search_name = st.text_input("Search Competitor Name")

            if search_name:
                filtered_data = filtered_data[
                    filtered_data["name"].str.contains(
                        search_name,
                        case=False,
                        na=False,
                    )
                ]

            st.dataframe(
                filtered_data,
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("### Stable Ranking Competitors")

        if not stable_players.empty:
            st.dataframe(
                stable_players,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No stable ranking competitors found.")

    # -------------------------------------------------
    # TAB 4: SQL QUERY CENTER
    # -------------------------------------------------

    with tab4:
        render_section_header(
            "SQL Query Center",
            "Explore the six analytical queries implemented for Rankings",
        )

        query_options = {
            "1. All Competitors with Rank and Points":
                repository.query_1_competitors_rank_points,

            "2. Top 5 Competitors":
                repository.query_2_top_5_competitors,

            "3. Stable Rank Competitors":
                repository.query_3_stable_rank_competitors,

            "5. Competitors per Country":
                repository.query_5_competitors_per_country,

            "6. Highest Points Competitors":
                repository.query_6_highest_points_competitors,
        }

        selected_query = st.selectbox(
            "Select Analytical Query",
            list(query_options.keys()),
        )

        if selected_query.startswith("4."):
            st.info("Use the Competitions Played vs Points chart in the Leaderboard tab for Query 4.")
        else:
            result = query_options[selected_query]()

            st.dataframe(
                result,
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("### Points by Country")

        selected_country = st.text_input(
            "Enter Country Name",
            value="Croatia",
        )

        if st.button("Run Country Query"):
            country_result = repository.query_4_points_by_country(
                selected_country
            )

            st.dataframe(
                country_result,
                use_container_width=True,
                hide_index=True,
            )

except Exception as error:
    st.error(f"Unable to load Rankings dashboard: {error}")
    st.exception(error)