"""CourtIQ Relational Database Manager.

Provides centralized database connection handling, ACID transactions,
parameterized query execution, and migration management for SQLite
(with ANSI SQL dialect compatibility for PostgreSQL / MySQL).
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Sequence, Union
import pandas as pd

from courtiq.core.config import get_settings
from courtiq.core.exceptions import DatabaseError, MigrationError
from courtiq.core.logging_config import get_logger

logger = get_logger("core.database")


class DatabaseManager:
    """Manages SQLite database connections, transactions, and migrations."""

    def __init__(self, db_path: Optional[Union[str, Path]] = None) -> None:
        """Initialize DatabaseManager.

        Args:
            db_path: Path to SQLite database file. If omitted, uses Settings.courtiq_db_path.
        """
        settings = get_settings()
        self.db_path = Path(db_path) if db_path else settings.courtiq_db_path
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._migrations_dir = settings.migrations_dir

    def get_connection(self) -> sqlite3.Connection:
        """Create and configure a new SQLite connection.

        Returns:
            Configured sqlite3.Connection instance with foreign keys enabled.
        """
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=20.0,
                check_same_thread=False,
            )
            conn.row_factory = sqlite3.Row
            # Enforce foreign key constraints
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as e:
            logger.error("Failed to connect to database at %s: %s", self.db_path, e)
            raise DatabaseError(f"Database connection error: {e}") from e

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager yielding an active database connection."""
        conn = self.get_connection()
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager yielding a connection within an atomic transaction.

        Commits on normal exit, rolls back on exception.
        """
        conn = self.get_connection()
        try:
            conn.execute("BEGIN TRANSACTION;")
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error("Transaction rolled back due to error: %s", e)
            raise DatabaseError(f"Transaction failed: {e}") from e
        finally:
            conn.close()

    def execute(self, query: str, params: Sequence[Any] = ()) -> int:
        """Execute a parameterized query inside an atomic transaction.

        Args:
            query: SQL statement with parameter placeholders (?).
            params: Sequence of parameter values.

        Returns:
            The number of affected rows.
        """
        with self.transaction() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.rowcount

    def execute_many(self, query: str, seq_of_params: Sequence[Sequence[Any]]) -> int:
        """Execute a parameterized query across multiple parameter sequences.

        Args:
            query: SQL statement.
            seq_of_params: Sequence of parameter tuples.

        Returns:
            Number of affected rows.
        """
        with self.transaction() as conn:
            cur = conn.cursor()
            cur.executemany(query, seq_of_params)
            return cur.rowcount

    def fetch_all(self, query: str, params: Sequence[Any] = ()) -> List[Dict[str, Any]]:
        """Execute query and return all matching records as dictionaries.

        Args:
            query: SQL SELECT query.
            params: Query parameters.

        Returns:
            List of row dictionaries.
        """
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()
            return [dict(row) for row in rows]

    def fetch_one(self, query: str, params: Sequence[Any] = ()) -> Optional[Dict[str, Any]]:
        """Execute query and return first matching record as dictionary.

        Args:
            query: SQL SELECT query.
            params: Query parameters.

        Returns:
            Row dictionary or None if no record found.
        """
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None

    def fetch_df(self, query: str, params: Sequence[Any] = ()) -> pd.DataFrame:
        """Execute query and return results directly as a Pandas DataFrame.

        Args:
            query: SQL SELECT query.
            params: Query parameters.

        Returns:
            Pandas DataFrame.
        """
        with self.connection() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def run_migrations(self, migrations_dir: Optional[Path] = None) -> List[str]:
        """Apply pending SQL migration scripts from the migrations directory.

        Args:
            migrations_dir: Directory containing .sql migration scripts.

        Returns:
            List of applied migration filenames.
        """
        target_dir = migrations_dir or self._migrations_dir
        if not target_dir.exists():
            logger.warning("Migrations directory %s does not exist.", target_dir)
            return []

        applied_migrations: List[str] = []
        with self.transaction() as conn:
            # Create schema_migrations tracking table if absent
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(50) PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Fetch already applied versions
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_migrations;")
            existing_versions = {row[0] for row in cursor.fetchall()}

            # Discover and sort migration files (e.g. 001_competitions.sql)
            migration_files = sorted(target_dir.glob("*.sql"))
            for sql_file in migration_files:
                version = sql_file.name
                if version not in existing_versions:
                    logger.info("Applying migration: %s", version)
                    try:
                        sql_script = sql_file.read_text(encoding="utf-8")
                        conn.executescript(sql_script)
                        conn.execute(
                            "INSERT INTO schema_migrations (version) VALUES (?);", (version,)
                        )
                        applied_migrations.append(version)
                    except Exception as e:
                        logger.error("Failed to apply migration %s: %s", version, e)
                        raise MigrationError(f"Migration {version} failed: {e}") from e

        if applied_migrations:
            logger.info("Successfully applied %d migrations: %s", len(applied_migrations), applied_migrations)
        else:
            logger.debug("Database schema is up to date. No new migrations.")
        return applied_migrations


_DB_INSTANCE: Optional[DatabaseManager] = None


def get_db(db_path: Optional[Union[str, Path]] = None) -> DatabaseManager:
    """Return singleton DatabaseManager instance."""
    global _DB_INSTANCE
    if _DB_INSTANCE is None or db_path is not None:
        _DB_INSTANCE = DatabaseManager(db_path)
    return _DB_INSTANCE
