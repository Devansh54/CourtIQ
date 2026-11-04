"""CourtIQ: Competitions & Categories Explorer.

Domain Contributor: Devansh (50% Milestone)
Features: Hierarchy navigation, category analytics, distribution charts,
interactive multi-filters, and verified execution of all 7 required SQL queries.
"""

import sys
from pathlib import Path

# Add src to sys.path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

import streamlit as st
import pandas as pd
from courtiq.core.database import get_db
from courtiq.domains.competitions.analytics import CompetitionsAnalytics
from courtiq.domains.competitions.repository import CompetitionsRepository
from courtiq.ingestion.runner import IngestionRunner
from courtiq.utils.formatting import apply_custom_css, render_metric_card, render_section_header

st.set_page_config(page_title="Competitions Explorer | CourtIQ", page_icon="🏆", layout="wide")
apply_custom_css()

db = get_db()
repo = CompetitionsRepository(db)
analytics = CompetitionsAnalytics(repo)

st.title("🏆 Tennis Competitions & Categories Explorer")
st.caption("Module Owner: Devansh — Explore tournament structures, formats, hierarchies, and analytical queries.")

# ------------------------------------------------------------------------------
# Empty State Check
# ------------------------------------------------------------------------------
if repo.get_competition_count() == 0:
    st.info("ℹ️ Competitions table is currently empty. Run ingestion to populate tournament data.")
    if st.button("🚀 Ingest Competitions Now", type="primary"):
        with st.spinner("Applying migrations and ingesting data..."):
            runner = IngestionRunner(db)
            res = runner.ingest_competitions()
            if res.status == "SUCCESS":
                st.success("Competitions successfully ingested!")
                st.rerun()
            else:
                st.error(f"Ingestion failed: {res.message}")
    st.stop()

# ------------------------------------------------------------------------------
# Domain KPIs
# ------------------------------------------------------------------------------
kpis = analytics.get_summary_kpis()
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_metric_card("Total Competitions", kpis["total_competitions"], "All Tournaments")
with c2:
    render_metric_card("Categories", kpis["total_categories"], "Governing Bodies")
with c3:
    render_metric_card("Doubles Events", kpis["doubles_count"], "Format: Doubles")
with c4:
    render_metric_card("Singles Events", kpis["singles_count"], "Format: Singles")
with c5:
    render_metric_card("Sub-Competitions", kpis["sub_competitions"], "Qualifying & Branches")

# ------------------------------------------------------------------------------
# Tabs: Overview Analytics, Hierarchy Explorer, Search, SQL Verification
# ------------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Distribution Analytics",
    "🌳 Hierarchy Explorer",
    "🔍 Filter & Search",
    "⚡ Required SQL Queries (Q1–Q7)",
])

# ------------------------------------------------------------------------------
# TAB 1: Distribution Analytics
# ------------------------------------------------------------------------------
with tab1:
    render_section_header("Competition & Category Distributions")
    chart_col1, chart_col2 = st.columns([3, 2])
    with chart_col1:
        st.plotly_chart(analytics.create_category_bar_chart(), use_container_width=True)
    with chart_col2:
        st.plotly_chart(analytics.create_type_sunburst_or_pie(), use_container_width=True)

    st.plotly_chart(analytics.create_type_distribution_stacked_bar(), use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 2: Hierarchy Explorer
# ------------------------------------------------------------------------------
with tab2:
    render_section_header("Parent-Child Competition Hierarchies", "Identify parent tournaments and their sub-competitions (REQ-COMP-11)")
    hierarchy_df = repo.query_5_parent_sub_hierarchy()
    if hierarchy_df.empty:
        st.write("No parent-sub competition relationships found in current data.")
    else:
        st.dataframe(
            hierarchy_df,
            use_container_width=True,
            column_config={
                "parent_name": "Parent Tournament",
                "sub_competition_name": "Sub-Competition / Event",
                "sub_type": "Format",
                "sub_gender": "Gender",
                "category_name": "Category",
            },
            hide_index=True,
        )

# ------------------------------------------------------------------------------
# TAB 3: Interactive Filter & Search
# ------------------------------------------------------------------------------
with tab3:
    render_section_header("Filter & Search Competitions")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    categories = repo.get_all_categories()
    cat_options = ["All"] + [c["category_name"] for c in categories]
    cat_id_map = {c["category_name"]: c["category_id"] for c in categories}

    with f_col1:
        search_kw = st.text_input("Search Tournament Name", placeholder="e.g. Vienna, Australian Open...")
    with f_col2:
        selected_cat = st.selectbox("Category", cat_options)
    with f_col3:
        selected_type = st.selectbox("Format", ["All", "singles", "doubles"])
    with f_col4:
        selected_gender = st.selectbox("Gender", ["All", "men", "women"])

    filter_cat_id = cat_id_map.get(selected_cat) if selected_cat != "All" else None
    filtered_df = repo.search_competitions(
        search_query=search_kw,
        category_id=filter_cat_id,
        comp_type=selected_type if selected_type != "All" else None,
        gender=selected_gender if selected_gender != "All" else None,
    )

    st.write(f"Showing **{len(filtered_df)}** matching competitions:")
    st.dataframe(
        filtered_df,
        use_container_width=True,
        column_config={
            "competition_name": "Competition Name",
            "category_name": "Category",
            "type": "Type",
            "gender": "Gender",
            "parent_name": "Parent Tournament",
        },
        hide_index=True,
    )

# ------------------------------------------------------------------------------
# TAB 4: Required SQL Queries Execution & Verification
# ------------------------------------------------------------------------------
with tab4:
    render_section_header(
        "Project Guide Mandated SQL Queries (1 Through 7)",
        "Every query defined in the project specification verified in real-time against the relational database."
    )

    query_selection = st.selectbox(
        "Select Mandated SQL Query to Inspect & Execute:",
        [
            "1. List all competitions along with their category name",
            "2. Count the number of competitions in each category",
            "3. Find all competitions of type 'doubles'",
            "4. Get competitions that belong to a specific category (e.g. ITF Men)",
            "5. Identify parent competitions and their sub-competitions",
            "6. Analyze the distribution of competition types by category",
            "7. List all competitions with no parent (top-level competitions)",
        ],
    )

    query_num = int(query_selection.split(".")[0])

    if query_num == 1:
        q_sql = repo._read_query("q1_list_with_category.sql")
        q_df = repo.query_1_all_with_category()
    elif query_num == 2:
        q_sql = repo._read_query("q2_count_by_category.sql")
        q_df = repo.query_2_count_by_category()
    elif query_num == 3:
        q_sql = repo._read_query("q3_doubles_competitions.sql")
        q_df = repo.query_3_doubles_competitions()
    elif query_num == 4:
        target_cat = st.text_input("Enter category name for Query 4:", value="ITF Men")
        q_sql = repo._read_query("q4_by_specific_category.sql")
        q_df = repo.query_4_by_category(target_cat)
    elif query_num == 5:
        q_sql = repo._read_query("q5_parent_sub_hierarchy.sql")
        q_df = repo.query_5_parent_sub_hierarchy()
    elif query_num == 6:
        q_sql = repo._read_query("q6_type_distribution_by_category.sql")
        q_df = repo.query_6_type_distribution_by_category()
    elif query_num == 7:
        q_sql = repo._read_query("q7_top_level_competitions.sql")
        q_df = repo.query_7_top_level_competitions()

    st.markdown("#### SQL Statement Executed:")
    st.code(q_sql, language="sql")

    st.markdown(f"#### Execution Output ({len(q_df)} rows returned):")
    st.dataframe(q_df, use_container_width=True, hide_index=True)
