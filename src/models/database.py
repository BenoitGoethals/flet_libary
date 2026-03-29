"""Async database engine and session management using SQLAlchemy.

Supports SQLite (via aiosqlite) and MSSQL (via aioodbc) backends
transparently. The backend is determined by the connection URL.
"""

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class Database:
    """Singleton async database manager providing SQLAlchemy engine and session factory.

    Attributes:
        _instance: Class-level singleton instance.
    """

    _instance: "Database | None" = None

    def __init__(self, db_url: str | None = None):
        """Initialize the async database manager.

        Args:
            db_url: SQLAlchemy async database URL. Defaults to config.DATABASE_URL.
                Supported schemes:
                - sqlite+aiosqlite:///path/to/file.db
                - mssql+aioodbc://user:pass@server/db?driver=...
        """
        if db_url is None:
            from config import DATABASE_URL
            db_url = DATABASE_URL

        self._db_url = db_url
        self._is_sqlite = "sqlite" in db_url

        self._engine: AsyncEngine = create_async_engine(db_url, echo=False)

        if self._is_sqlite:
            self._register_sqlite_pragmas()

        self._session_factory = async_sessionmaker(
            bind=self._engine, expire_on_commit=False, class_=AsyncSession
        )

    def _register_sqlite_pragmas(self):
        """Enable foreign key enforcement for SQLite connections."""

        @event.listens_for(self._engine.sync_engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    @classmethod
    def instance(cls) -> "Database":
        """Get or create the singleton Database instance.

        Returns:
            The shared Database instance.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance. Useful for testing."""
        cls._instance = None

    @property
    def is_sqlite(self) -> bool:
        """Check if the current backend is SQLite."""
        return self._is_sqlite

    @property
    def is_mssql(self) -> bool:
        """Check if the current backend is MSSQL."""
        return "mssql" in self._db_url

    def create_session(self) -> AsyncSession:
        """Create and return a new async SQLAlchemy session.

        Returns:
            A new AsyncSession instance.
        """
        return self._session_factory()

    async def init_schema(self):
        """Create all tables defined in the ORM Base metadata."""
        from models.entities import Base

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self):
        """Drop all tables. Used for testing teardown."""
        from models.entities import Base

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def dispose(self):
        """Dispose of the engine connection pool."""
        await self._engine.dispose()
