"""Shared fixtures for integration tests using an in-memory SQLite database."""

import pytest
from models.database import Database
from services.container import ServiceContainer


@pytest.fixture()
def db():
    """Create a fresh in-memory SQLite database for each test.

    Yields:
        A Database instance backed by in-memory SQLite.
    """
    database = Database("sqlite:///:memory:")
    database.init_schema()
    yield database
    database.drop_all()


@pytest.fixture()
def container(db):
    """Create a ServiceContainer wired to the in-memory test database.

    Args:
        db: The test Database fixture.

    Yields:
        A fully wired ServiceContainer.
    """
    yield ServiceContainer(database=db)
