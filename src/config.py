"""Application configuration for database and environment settings.

Supports switching between SQLite (default/development) and MSSQL (production)
via the DATABASE_URL environment variable. Uses async drivers.

Examples:
    SQLite (default, async via aiosqlite):
        DATABASE_URL=sqlite+aiosqlite:///library.db

    MSSQL with aioodbc:
        DATABASE_URL=mssql+aioodbc://user:pass@server/dbname?driver=ODBC+Driver+18+for+SQL+Server

    MSSQL with asyncpg (via mssql dialect):
        DATABASE_URL=mssql+pyodbc://user:pass@server/dbname?driver=...
"""

import os

# The database URL. Set via environment variable or defaults to async SQLite.
DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{os.path.join(os.path.dirname(__file__), 'library.db')}",
)
