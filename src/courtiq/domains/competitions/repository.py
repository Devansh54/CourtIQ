"""CourtIQ Competitions Relational Repository.

Handles database persistence, idempotent upserts, and analytical queries
for categories and competitions domains.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from courtiq.core.config import get_settings
from courtiq.core.database import DatabaseManager, get_db
from courtiq.core.logging_config import get_logger
from courtiq.domains.competitions.schemas import Category, Competition

logger = get_logger("domains.competitions.repository")


class CompetitionsRepository:
    """Repository managing SQL persistence and analytics for competitions and categories."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None) -> None:
        """Initialize CompetitionsRepository.

        Args:
            db_manager: DatabaseManager instance. If None, uses default get_db().
        """
        self.db = db_manager or get_db()
        self._queries_dir = get_settings().project_root / "sql" / "queries" / "competitions"

    def _read_query(self, filename: str) -> str:
        """Load SQL query text from file."""
        file_path = self._queries_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"SQL query file not found: {file_path}")
        return file_path.read_text(encoding="utf-8")

    # --------------------------------------------------------------------------
    # Persistence Methods (Idempotent Upsert)
    # --------------------------------------------------------------------------

    def save_categories(self, categories: List[Category]) -> int:
        """Persist a list of categories using idempotent INSERT ON CONFLICT DO UPDATE.

        Args:
            categories: List of validated Category entities.

        Returns:
            Count of persisted categories.
        """
        if not categories:
            return 0

        query = """
            INSERT INTO categories (category_id, category_name)
            VALUES (:category_id, :category_name)
            ON CONFLICT (category_id) DO UPDATE SET
                category_name = EXCLUDED.category_name;
        """
        params = [
            {"category_id": cat.category_id, "category_name": cat.category_name}
            for cat in categories
        ]
        logger.info("Persisting %d categories to database.", len(categories))
        return self.db.execute_many(query, params)

    def save_competitions(self, competitions: List[Competition]) -> int:
        """Persist a list of competitions using idempotent INSERT ON CONFLICT DO UPDATE.

        Args:
            competitions: List of validated Competition entities.

        Returns:
            Count of persisted competitions.
        """
        if not competitions:
            return 0

        # Enforce insertion order: top-level parents first, then sub-competitions,
        # to respect referential integrity when self-referencing foreign keys are active.
        parents = [c for c in competitions if not c.parent_id]
        children = [c for c in competitions if c.parent_id]
        ordered_competitions = parents + children

        query = """
            INSERT INTO competitions (
                competition_id, competition_name, parent_id, type, gender, category_id
            )
            VALUES (
                :competition_id, :competition_name, :parent_id, :type, :gender, :category_id
            )
            ON CONFLICT (competition_id) DO UPDATE SET
                competition_name = EXCLUDED.competition_name,
                parent_id = EXCLUDED.parent_id,
                type = EXCLUDED.type,
                gender = EXCLUDED.gender,
                category_id = EXCLUDED.category_id;
        """
        params = [
            {
                "competition_id": c.competition_id,
                "competition_name": c.competition_name,
                "parent_id": c.parent_id,
                "type": c.type,
                "gender": c.gender,
                "category_id": c.category_id,
            }
            for c in ordered_competitions
        ]
        logger.info("Persisting %d competitions to database (%d parents, %d sub-competitions).",
                    len(competitions), len(parents), len(children))
        return self.db.execute_many(query, params)

    # --------------------------------------------------------------------------
    # Core Metadata Queries
    # --------------------------------------------------------------------------

    def get_category_count(self) -> int:
        """Return total count of categories in the database."""
        row = self.db.fetch_one("SELECT COUNT(*) AS count FROM categories;")
        return row["count"] if row else 0

    def get_competition_count(self) -> int:
        """Return total count of competitions in the database."""
        row = self.db.fetch_one("SELECT COUNT(*) AS count FROM competitions;")
        return row["count"] if row else 0

    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Return all categories sorted by name."""
        return self.db.fetch_all("SELECT category_id, category_name FROM categories ORDER BY category_name;")

    # --------------------------------------------------------------------------
    # Required Project Guide SQL Queries (1 Through 7)
    # --------------------------------------------------------------------------

    def query_1_all_with_category(self) -> pd.DataFrame:
        """Execute Query 1: List all competitions along with their category name."""
        sql = self._read_query("q1_list_with_category.sql")
        return self.db.fetch_df(sql)

    def query_2_count_by_category(self) -> pd.DataFrame:
        """Execute Query 2: Count the number of competitions in each category."""
        sql = self._read_query("q2_count_by_category.sql")
        return self.db.fetch_df(sql)

    def query_3_doubles_competitions(self) -> pd.DataFrame:
        """Execute Query 3: Find all competitions of type 'doubles'."""
        sql = self._read_query("q3_doubles_competitions.sql")
        return self.db.fetch_df(sql)

    def query_4_by_category(self, category_target: str) -> pd.DataFrame:
        """Execute Query 4: Get competitions that belong to a specific category (e.g. ITF Men).

        Args:
            category_target: Category name (e.g. 'ITF Men') or ID.
        """
        sql = self._read_query("q4_by_specific_category.sql")
        return self.db.fetch_df(sql, params={"category_target": category_target})

    def query_5_parent_sub_hierarchy(self) -> pd.DataFrame:
        """Execute Query 5: Identify parent competitions and their sub-competitions."""
        sql = self._read_query("q5_parent_sub_hierarchy.sql")
        return self.db.fetch_df(sql)

    def query_6_type_distribution_by_category(self) -> pd.DataFrame:
        """Execute Query 6: Analyze the distribution of competition types by category."""
        sql = self._read_query("q6_type_distribution_by_category.sql")
        return self.db.fetch_df(sql)

    def query_7_top_level_competitions(self) -> pd.DataFrame:
        """Execute Query 7: List all competitions with no parent (top-level competitions)."""
        sql = self._read_query("q7_top_level_competitions.sql")
        return self.db.fetch_df(sql)

    # --------------------------------------------------------------------------
    # Interactive Search & Multi-Filter Query
    # --------------------------------------------------------------------------

    def search_competitions(
        self,
        search_query: Optional[str] = None,
        category_id: Optional[str] = None,
        comp_type: Optional[str] = None,
        gender: Optional[str] = None,
    ) -> pd.DataFrame:
        """Search and filter competitions dynamically with parameterized SQL."""
        base_sql = """
            SELECT 
                c.competition_id,
                c.competition_name,
                c.parent_id,
                p.competition_name AS parent_name,
                c.type,
                c.gender,
                c.category_id,
                cat.category_name
            FROM competitions c
            JOIN categories cat ON c.category_id = cat.category_id
            LEFT JOIN competitions p ON c.parent_id = p.competition_id
            WHERE 1=1
        """
        params: Dict[str, Any] = {}

        if search_query and search_query.strip():
            base_sql += " AND (LOWER(c.competition_name) LIKE :search_kw OR LOWER(cat.category_name) LIKE :search_kw)"
            params["search_kw"] = f"%{search_query.strip().lower()}%"

        if category_id and category_id != "All":
            base_sql += " AND c.category_id = :category_id"
            params["category_id"] = category_id

        if comp_type and comp_type != "All":
            base_sql += " AND LOWER(c.type) = LOWER(:comp_type)"
            params["comp_type"] = comp_type

        if gender and gender != "All":
            base_sql += " AND LOWER(c.gender) = LOWER(:gender)"
            params["gender"] = gender

        base_sql += " ORDER BY cat.category_name ASC, c.competition_name ASC;"
        return self.db.fetch_df(base_sql, params=params)
