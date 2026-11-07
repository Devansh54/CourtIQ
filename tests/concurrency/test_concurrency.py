"""Concurrency and Multi-User Load Tests for CourtIQ DatabaseManager.

Simulates multi-user Streamlit dashboard traffic and concurrent database operations
to ensure the connection pool (QueuePool) operates without exhaustion, leaks, or deadlocks.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import pytest
from courtiq.core.database import DatabaseManager
from courtiq.domains.competitions.repository import CompetitionsRepository
from courtiq.domains.competitions.schemas import Category, Competition


def test_concurrent_read_queries(postgres_test_db: DatabaseManager, sample_competitions_payload):
    """Verify that multiple concurrent threads can query the PostgreSQL database simultaneously."""
    assert postgres_test_db.is_postgres is True, "Concurrency test must run against PostgreSQL"
    from courtiq.domains.competitions.transformer import CompetitionsTransformer

    # Seed test database
    transformer = CompetitionsTransformer()
    categories, competitions = transformer.transform(sample_competitions_payload)
    repo = CompetitionsRepository(postgres_test_db)
    repo.save_categories(categories)
    repo.save_competitions(competitions)

    num_threads = 12
    iterations_per_thread = 5

    def worker_read_task(worker_id: int) -> int:
        local_repo = CompetitionsRepository(postgres_test_db)
        total_rows_fetched = 0
        for _ in range(iterations_per_thread):
            # Alternate through the various analytical queries
            df1 = local_repo.query_1_all_with_category()
            total_rows_fetched += len(df1)

            df2 = local_repo.query_2_count_by_category()
            total_rows_fetched += len(df2)

            df3 = local_repo.query_3_doubles_competitions()
            total_rows_fetched += len(df3)

            df7 = local_repo.query_7_top_level_competitions()
            total_rows_fetched += len(df7)
        return total_rows_fetched

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker_read_task, i) for i in range(num_threads)]
        results = [f.result() for f in as_completed(futures)]

    assert len(results) == num_threads
    assert all(r > 0 for r in results)


def test_concurrent_isolated_transactions(postgres_test_db: DatabaseManager):
    """Verify that concurrent writes in isolated transactions succeed without deadlock on PostgreSQL."""
    assert postgres_test_db.is_postgres is True, "Concurrency test must run against PostgreSQL"
    num_threads = 8

    def worker_write_task(worker_id: int) -> str:
        cat_id = f"sr:cat:concurrent_{worker_id}"
        cat_name = f"Concurrent Category {worker_id}"

        # Write inside transaction
        postgres_test_db.execute(
            "INSERT INTO categories (category_id, category_name) VALUES (:id, :name) "
            "ON CONFLICT (category_id) DO UPDATE SET category_name = EXCLUDED.category_name;",
            {"id": cat_id, "name": cat_name},
        )

        # Immediate read-back
        row = postgres_test_db.fetch_one(
            "SELECT category_name FROM categories WHERE category_id = :id;",
            {"id": cat_id},
        )
        assert row is not None
        return row["category_name"]

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker_write_task, i) for i in range(num_threads)]
        results = [f.result() for f in as_completed(futures)]

    assert len(results) == num_threads
    for i in range(num_threads):
        assert f"Concurrent Category {i}" in results

