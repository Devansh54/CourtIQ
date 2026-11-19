"""CourtIQ Phase 3 Application & Analytics Verification Script.

Executes all 7 analytical SQL queries, search filters, and analytics services
using the runtime application account 'courtiq_app' against PostgreSQL 18.6.
"""

import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from courtiq.core.config import get_settings
from courtiq.core.database import DatabaseManager
from courtiq.domains.competitions.repository import CompetitionsRepository
from courtiq.domains.competitions.analytics import CompetitionsAnalytics

def main():
    print("=" * 65)
    print("COURTIQ — PHASE 3 APPLICATION & ANALYTICS VERIFICATION")
    print("=" * 65)

    settings = get_settings()
    print(f"Target Database URL: {settings.database_url.split('@')[-1]}")
    
    db_mgr = DatabaseManager(settings.database_url)
    repo = CompetitionsRepository(db_mgr)
    analytics = CompetitionsAnalytics(repo)

    # 1. Verify PostgreSQL dialect
    print("\n--- 1. Engine & Dialect Verification ---")
    print(f"[CHECK] Dialect name:  {db_mgr._engine.dialect.name}")
    print(f"[CHECK] Is PostgreSQL: {db_mgr.is_postgres}")
    print(f"[CHECK] Is SQLite:     {db_mgr.is_sqlite}")
    assert db_mgr.is_sqlite is False, "DatabaseManager is running on SQLite, expected PostgreSQL!"
    assert db_mgr.is_postgres is True, "DatabaseManager is not reporting PostgreSQL!"
    assert db_mgr._engine.dialect.name == "postgresql", f"Expected postgresql, got {db_mgr._engine.dialect.name}"
    print("[PASS] Confirmed PostgreSQL dialect in active use (no SQLite fallback).")

    # 2. Verify all 7 Analytical SQL Queries
    print("\n--- 2. Required 7 SQL Queries Execution ---")
    
    # Q1: All with category
    df_q1 = repo.query_1_all_with_category()
    print(f"[Q1] All Competitions with Category: {len(df_q1)} rows returned.")
    assert len(df_q1) == 19, f"Expected 19 rows in Q1, got {len(df_q1)}"
    assert "category_name" in df_q1.columns
    print("     Sample row:", df_q1.iloc[0][["competition_name", "category_name", "type"]].to_dict())

    # Q2: Count by category
    df_q2 = repo.query_2_count_by_category()
    print(f"[Q2] Count by Category: {len(df_q2)} categories returned.")
    assert len(df_q2) == 5, f"Expected 5 categories in Q2, got {len(df_q2)}"
    print("     Counts:\n" + df_q2.to_string(index=False))

    # Q3: Doubles competitions
    df_q3 = repo.query_3_doubles_competitions()
    print(f"[Q3] Doubles Competitions: {len(df_q3)} rows returned.")
    assert len(df_q3) > 0, "Expected doubles competitions"
    assert all(df_q3["type"].str.lower() == "doubles"), "Non-doubles found in Q3!"

    # Q4: Specific category (e.g. Grand Slam)
    df_q4 = repo.query_4_by_category("Grand Slam")
    print(f"[Q4] Competitions by Category ('Grand Slam'): {len(df_q4)} rows returned.")
    assert len(df_q4) == 8, f"Expected 8 Grand Slam competitions, got {len(df_q4)}"

    # Q5: Parent / Sub-competition hierarchy
    df_q5 = repo.query_5_parent_sub_hierarchy()
    print(f"[Q5] Parent / Sub Hierarchy: {len(df_q5)} rows returned.")
    assert len(df_q5) == 9, f"Expected 9 sub-competitions with parents in Q5, got {len(df_q5)}"
    assert "parent_name" in df_q5.columns

    # Q6: Type distribution by category
    df_q6 = repo.query_6_type_distribution_by_category()
    print(f"[Q6] Type Distribution by Category: {len(df_q6)} distribution rows returned.")
    assert len(df_q6) > 0

    # Q7: Top-level competitions
    df_q7 = repo.query_7_top_level_competitions()
    print(f"[Q7] Top-Level Competitions (parent_id IS NULL): {len(df_q7)} rows returned.")
    assert len(df_q7) == 10, f"Expected 10 top-level competitions, got {len(df_q7)}"

    # 3. Dynamic Search & Filters
    print("\n--- 3. Dynamic Multi-Filter Search ---")
    # Search by keyword
    df_search_wim = repo.search_competitions(search_query="Wimbledon")
    print(f"[Search 'Wimbledon']: {len(df_search_wim)} matches found.")
    assert len(df_search_wim) >= 1, "Expected Wimbledon competitions"
    print("     Matches:", df_search_wim["competition_name"].tolist())

    # Filter by category + gender
    df_filtered = repo.search_competitions(category_id="sr:category:1", gender="men")
    print(f"[Filter ATP Men]: {len(df_filtered)} matches found.")
    assert len(df_filtered) == 4

    # 4. Analytics & KPIs
    print("\n--- 4. Analytics KPIs & Visualizations ---")
    kpis = analytics.get_summary_kpis()
    print("KPIs:", kpis)
    assert kpis["total_competitions"] == 19
    assert kpis["total_categories"] == 5
    assert kpis["doubles_count"] == 8
    assert kpis["singles_count"] == 11
    assert kpis["parent_competitions"] == 10
    assert kpis["sub_competitions"] == 9

    fig_bar = analytics.create_category_bar_chart()
    assert fig_bar is not None
    print("[PASS] Generated Plotly Category Bar Chart successfully.")

    fig_pie = analytics.create_type_sunburst_or_pie()
    assert fig_pie is not None
    print("[PASS] Generated Plotly Type Sunburst/Pie Chart successfully.")

    fig_stacked = analytics.create_type_distribution_stacked_bar()
    assert fig_stacked is not None
    print("[PASS] Generated Plotly Type Distribution Stacked Bar Chart successfully.")

    db_mgr._engine.dispose()
    print("\n" + "=" * 65)
    print("[PASS] ALL APPLICATION & ANALYTICS VERIFICATIONS PASSED")
    print("=" * 65)
    return 0

if __name__ == "__main__":
    sys.exit(main())
