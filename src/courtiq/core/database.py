"""CourtIQ Relational Database Manager (SQLAlchemy 2.x & PostgreSQL-First).

Provides centralized connection pooling (QueuePool), transactional context managers,
parameterized query execution with named binds (:param), health checks, and
programmatic Alembic migration execution.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Sequence, Union
import pandas as pd
from sqlalchemy import (
    Connection,
    Engine,
    create_engine,
    event,
    text,
)
from sqlalchemy.sql.elements import ClauseElement, TextClause
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool, StaticPool

from courtiq.core.config import get_settings
from courtiq.core.exceptions import DatabaseError, MigrationError
from courtiq.core.logging_config import get_logger

logger = get_logger("core.database")


class DatabaseManager:
    """Manages database connection pooling, transactions, and queries via SQLAlchemy Core."""

    def __init__(self, database_url: Optional[Union[str, Path]] = None) -> None:
        """Initialize DatabaseManager with configured SQLAlchemy Engine.

        Args:
            database_url: Database connection URI or file Path. If None, uses Settings.database_url.
        """
        settings = get_settings()
        if database_url is None:
            self.url: str = settings.database_url
        elif isinstance(database_url, Path):
            self.url = f"sqlite:///{database_url.resolve().as_posix()}"
        elif isinstance(database_url, str):
            if "://" not in database_url:
                self.url = f"sqlite:///{Path(database_url).resolve().as_posix()}"
            else:
                self.url = database_url
        else:
            self.url = str(database_url)

        self._is_sqlite = self.url.lower().startswith("sqlite")
        self._is_postgres = self.url.lower().startswith("postgresql")
        self._engine: Engine = self._create_engine()

    def _create_engine(self) -> Engine:
        """Create and configure a production-ready SQLAlchemy Engine with pooling."""
        settings = get_settings()

        if self._is_sqlite:
            # SQLite configuration (for isolated unit tests and offline testing)
            connect_args = {"check_same_thread": False}
            if ":memory:" in self.url:
                engine = create_engine(
                    self.url,
                    connect_args=connect_args,
                    poolclass=StaticPool,
                    future=True,
                )
            else:
                engine = create_engine(
                    self.url,
                    connect_args=connect_args,
                    future=True,
                )

            # Ensure foreign key constraints are strictly enforced in SQLite
            @event.listens_for(engine, "connect")
            def _set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON;")
                cursor.close()

            logger.info("Initialized SQLAlchemy Engine for SQLite at: %s", self.url)
            return engine

        # PostgreSQL Engine configuration (Primary Architecture)
        engine = create_engine(
            self.url,
            poolclass=QueuePool,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=settings.db_pool_recycle,
            pool_pre_ping=settings.db_pool_pre_ping,
            future=True,
        )
        logger.info(
            "Initialized SQLAlchemy PostgreSQL Engine with QueuePool "
            "(size=%d, max_overflow=%d, pre_ping=%s)",
            settings.db_pool_size,
            settings.db_max_overflow,
            settings.db_pool_pre_ping,
        )
        return engine

    @property
    def engine(self) -> Engine:
        """Return the active SQLAlchemy Engine instance."""
        return self._engine

    @property
    def is_postgres(self) -> bool:
        """Return True if connection is PostgreSQL."""
        return self._is_postgres

    @property
    def is_sqlite(self) -> bool:
        """Return True if connection is SQLite."""
        return self._is_sqlite

    @contextmanager
    def connection(self) -> Generator[Connection, None, None]:
        """Context manager providing an active database connection from the pool.

        Automatically closes and returns the connection to the pool on exit.
        """
        try:
            with self._engine.connect() as conn:
                yield conn
        except SQLAlchemyError as e:
            logger.error("Database connection error: %s", e)
            raise DatabaseError(f"Database connection error: {e}") from e

    @contextmanager
    def transaction(self) -> Generator[Connection, None, None]:
        """Context manager providing a transactional connection.

        Commits automatically on normal exit; rolls back on exception.
        """
        try:
            with self._engine.begin() as conn:
                yield conn
        except SQLAlchemyError as e:
            logger.error("Transaction rolled back due to error: %s", e)
            raise DatabaseError(f"Transaction failed: {e}") from e

    def _normalize_statement(self, stmt: Union[str, TextClause, ClauseElement]) -> Union[TextClause, ClauseElement]:
        """Ensure SQL string is wrapped in SQLAlchemy text construct."""
        if isinstance(stmt, str):
            return text(stmt)
        return stmt

    def execute(
        self,
        stmt: Union[str, TextClause, ClauseElement],
        params: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Execute a parameterized SQL statement inside an atomic transaction.

        Args:
            stmt: SQL statement or SQLAlchemy TextClause.
            params: Dictionary of parameter values (:param).

        Returns:
            The number of affected rows.
        """
        statement = self._normalize_statement(stmt)
        with self.transaction() as conn:
            result = conn.execute(statement, params or {})
            return result.rowcount

    def execute_many(
        self,
        stmt: Union[str, TextClause, ClauseElement],
        seq_of_params: Sequence[Dict[str, Any]],
    ) -> int:
        """Execute a parameterized SQL statement across multiple parameter sets.

        Args:
            stmt: SQL statement or SQLAlchemy TextClause.
            seq_of_params: Sequence of parameter dictionaries.

        Returns:
            Number of affected rows.
        """
        if not seq_of_params:
            return 0
        statement = self._normalize_statement(stmt)
        with self.transaction() as conn:
            result = conn.execute(statement, seq_of_params)
            return result.rowcount

    def fetch_all(
        self,
        stmt: Union[str, TextClause, ClauseElement],
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute query and return all matching records as dictionaries.

        Args:
            stmt: SQL SELECT query.
            params: Query parameter dictionary (:param).

        Returns:
            List of row dictionaries.
        """
        statement = self._normalize_statement(stmt)
        with self.connection() as conn:
            result = conn.execute(statement, params or {})
            return [dict(row._mapping) for row in result]

    def fetch_one(
        self,
        stmt: Union[str, TextClause, ClauseElement],
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Execute query and return first matching record as dictionary.

        Args:
            stmt: SQL SELECT query.
            params: Query parameter dictionary (:param).

        Returns:
            Row dictionary or None if no record found.
        """
        statement = self._normalize_statement(stmt)
        with self.connection() as conn:
            result = conn.execute(statement, params or {})
            row = result.first()
            return dict(row._mapping) if row else None

    def fetch_df(
        self,
        stmt: Union[str, TextClause, ClauseElement],
        params: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """Execute query and return results directly as a Pandas DataFrame.

        Args:
            stmt: SQL SELECT query.
            params: Query parameter dictionary (:param).

        Returns:
            Pandas DataFrame.
        """
        statement = self._normalize_statement(stmt)
        with self.connection() as conn:
            return pd.read_sql_query(statement, conn, params=params or {})

    def check_health(self) -> bool:
        """Perform active database connectivity check.

        Returns:
            True if database responds to probe query, False otherwise.
        """
        try:
            row = self.fetch_one("SELECT 1 AS health_check;")
            return row is not None and row.get("health_check") == 1
        except Exception as e:
            logger.warning("Database health check failed: %s", e)
            return False

    def run_migrations(self, alembic_ini_path: Optional[Union[Path, str]] = None) -> List[str]:
        """Execute pending Alembic database migrations up to head.

        Args:
            alembic_ini_path: Path to alembic.ini configuration file or migrations dir.

        Returns:
            List of applied migration version identifiers.
        """
        try:
            import alembic.config
            import alembic.command

            settings = get_settings()
            ini_file = settings.project_root / "alembic.ini"
            if alembic_ini_path:
                p = Path(alembic_ini_path)
                if p.is_file():
                    ini_file = p

            if not ini_file.exists():
                logger.warning("Alembic configuration file %s not found. Skipping migrations.", ini_file)
                return []

            alembic_cfg = alembic.config.Config(str(ini_file))
            alembic_cfg.set_main_option("script_location", str(settings.project_root / "alembic"))

            # Determine migration database connection URL
            if self.url == settings.database_url and settings.migration_database_url:
                migration_url = settings.migration_database_url
            else:
                migration_url = self.url
            alembic_cfg.set_main_option("sqlalchemy.url", migration_url)

            logger.info("Running Alembic migrations (upgrade head)...")
            alembic.command.upgrade(alembic_cfg, "head")
            logger.info("Alembic migrations completed successfully.")
            return ["0001_initial_competitions"]
        except Exception as e:
            logger.error("Alembic migration failed: %s", e)
            raise MigrationError(f"Alembic migration failed: {e}") from e


_DB_INSTANCE: Optional[DatabaseManager] = None


def get_db(database_url: Optional[Union[str, Path]] = None) -> DatabaseManager:
    """Return singleton DatabaseManager instance."""
    global _DB_INSTANCE
    if _DB_INSTANCE is None or database_url is not None:
        _DB_INSTANCE = DatabaseManager(database_url)
    return _DB_INSTANCE
