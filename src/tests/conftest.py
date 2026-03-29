"""Shared fixtures for async integration tests using an in-memory SQLite database."""

import pytest
import pytest_asyncio
from models.database import Database
from services.container import ServiceContainer


@pytest_asyncio.fixture()
async def db():
    """Create a fresh in-memory async SQLite database for each test.

    Yields:
        A Database instance backed by in-memory aiosqlite.
    """
    database = Database("sqlite+aiosqlite:///:memory:")
    await database.init_schema()
    yield database
    await database.drop_all()
    await database.dispose()


@pytest_asyncio.fixture()
async def container(db):
    """Create a ServiceContainer wired to the in-memory test database.

    Args:
        db: The test Database fixture.

    Yields:
        A fully wired ServiceContainer (schema already initialized).
    """
    c = ServiceContainer(database=db)
    yield c
