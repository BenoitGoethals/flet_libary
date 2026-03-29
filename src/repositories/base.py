"""Abstract base repository defining the async CRUD interface using SQLAlchemy sessions."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import Database

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base class for all entity repositories.

    Provides an async session helper and defines the CRUD contract
    that concrete repositories must implement.

    Args:
        T: The ORM model type managed by this repository.
    """

    def __init__(self, database: Database):
        """Initialize the repository with a database instance.

        Args:
            database: The Database instance used to create async sessions.
        """
        self._db = database

    def _session(self) -> AsyncSession:
        """Create and return a new async SQLAlchemy session.

        Returns:
            A new AsyncSession instance.
        """
        return self._db.create_session()

    @staticmethod
    def _detach(session: AsyncSession, objects: list) -> list:
        """Expunge objects from the session so they can be used after session close.

        Args:
            session: The active async SQLAlchemy session.
            objects: A list of ORM objects to expunge.

        Returns:
            The same list of objects, now detached.
        """
        for obj in objects:
            session.expunge(obj)
        return objects

    @staticmethod
    def _detach_one(session: AsyncSession, obj):
        """Expunge a single object from the session.

        Args:
            session: The active async SQLAlchemy session.
            obj: The ORM object to expunge.

        Returns:
            The detached object, or None if obj was None.
        """
        if obj is not None:
            session.expunge(obj)
        return obj

    @abstractmethod
    async def get_all(self) -> list[T]:
        """Retrieve all entities from the database.

        Returns:
            A list of all entities.
        """
        ...

    @abstractmethod
    async def add(self, entity: T) -> None:
        """Add a new entity to the database.

        Args:
            entity: The entity to persist.
        """
        ...

    @abstractmethod
    async def update(self, entity: T) -> None:
        """Update an existing entity in the database.

        Args:
            entity: The entity with updated fields. Must have a valid id.
        """
        ...

    @abstractmethod
    async def delete(self, entity_id: int) -> None:
        """Delete an entity from the database by its ID.

        Args:
            entity_id: The unique identifier of the entity to delete.
        """
        ...
