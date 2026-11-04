"""Unit tests for CompetitionsRepository and Mandated SQL Queries (1 to 7).

Verifies persistence, idempotency, and execution accuracy of all 7 queries
specified in the project guide.
"""

from courtiq.core.database import DatabaseManager
from courtiq.domains.competitions.repository import CompetitionsRepository
from courtiq.domains.competitions.transformer import CompetitionsTransformer


def test_repository_save_and_all_7_queries(test_db: DatabaseManager, sample_competitions_payload):
    """Verify data persistence and all 7 project guide SQL queries."""
    transformer = CompetitionsTransformer()
    categories, competitions = transformer.transform(sample_competitions_payload)

    repo = CompetitionsRepository(test_db)

    # 1. Test Persistence
    cats_saved = repo.save_categories(categories)
    comps_saved = repo.save_competitions(competitions)

    assert cats_saved == len(categories)
    assert comps_saved == len(competitions)
    assert repo.get_category_count() == len(categories)
    assert repo.get_competition_count() == len(competitions)

    # 2. Test Idempotency (Re-saving should succeed without duplicate or PK errors)
    cats_resaved = repo.save_categories(categories)
    comps_resaved = repo.save_competitions(competitions)
    assert repo.get_competition_count() == len(competitions)

    # 3. Query 1: List all competitions along with their category name
    df_q1 = repo.query_1_all_with_category()
    assert not df_q1.empty
    assert "category_name" in df_q1.columns
    assert "competition_name" in df_q1.columns
    assert len(df_q1) == len(competitions)

    # 4. Query 2: Count the number of competitions in each category
    df_q2 = repo.query_2_count_by_category()
    assert not df_q2.empty
    assert "competition_count" in df_q2.columns
    assert df_q2["competition_count"].sum() == len(competitions)

    # 5. Query 3: Find all competitions of type 'doubles'
    df_q3 = repo.query_3_doubles_competitions()
    assert not df_q3.empty
    assert all(t.lower() == "doubles" for t in df_q3["type"])
    assert len(df_q3) >= 5

    # 6. Query 4: Get competitions that belong to a specific category (e.g. 'ITF Men')
    df_q4 = repo.query_4_by_category("ITF Men")
    assert not df_q4.empty
    assert all(cat == "ITF Men" for cat in df_q4["category_name"])

    # 7. Query 5: Identify parent competitions and their sub-competitions
    df_q5 = repo.query_5_parent_sub_hierarchy()
    assert not df_q5.empty
    assert "parent_name" in df_q5.columns
    assert "sub_competition_name" in df_q5.columns
    assert len(df_q5) >= 5

    # 8. Query 6: Analyze the distribution of competition types by category
    df_q6 = repo.query_6_type_distribution_by_category()
    assert not df_q6.empty
    assert "category_name" in df_q6.columns
    assert "type" in df_q6.columns
    assert "competition_count" in df_q6.columns

    # 9. Query 7: List all competitions with no parent (top-level competitions)
    df_q7 = repo.query_7_top_level_competitions()
    assert not df_q7.empty
    # In Q7, all returned competitions must be top-level (no parent)
    top_level_ids = set(df_q7["competition_id"])
    parent_ids_in_all = {c.parent_id for c in competitions if c.parent_id}
    # Check that none of the top-level items are in children
    for comp in competitions:
        if comp.competition_id in top_level_ids:
            assert comp.parent_id is None
