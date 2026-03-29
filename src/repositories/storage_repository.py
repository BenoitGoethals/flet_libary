"""Async repository for Storage entity persistence and retrieval."""

from sqlalchemy import select, func
from models.entities import Storage, Book
from repositories.base import BaseRepository


class StorageRepository(BaseRepository[Storage]):
    """Handles all async database operations for Storage entities."""

    async def get_all(self) -> list[Storage]:
        """Retrieve all storage locations from the database.

        Returns:
            A list of all Storage entities ordered by name.
        """
        async with self._session() as session:
            stmt = select(Storage).order_by(Storage.name)
            result = await session.scalars(stmt)
            results = list(result.all())
            return self._detach(session, results)

    async def add(self, entity: Storage) -> None:
        """Insert a new storage location into the database.

        Args:
            entity: The Storage to persist.
        """
        async with self._session() as session:
            session.add(entity)
            await session.commit()

    async def update(self, entity: Storage) -> None:
        """Update an existing storage location's details.

        Args:
            entity: The Storage with updated fields. Must have a valid id.
        """
        async with self._session() as session:
            storage = await session.get(Storage, entity.id)
            if storage:
                storage.name = entity.name
                storage.location = entity.location
                storage.capacity = entity.capacity
                await session.commit()

    async def delete(self, entity_id: int) -> None:
        """Delete a storage location from the database.

        Args:
            entity_id: The ID of the storage to delete.
        """
        async with self._session() as session:
            storage = await session.get(Storage, entity_id)
            if storage:
                await session.delete(storage)
                await session.commit()

    async def get_book_count(self, storage_id: int) -> int:
        """Count the number of available books in a given storage.

        Args:
            storage_id: The ID of the storage to count books for.

        Returns:
            The number of available books in the specified storage.
        """
        async with self._session() as session:
            stmt = (
                select(func.count())
                .select_from(Book)
                .where(Book.storage_id == storage_id, Book.status == "available")
            )
            return await session.scalar(stmt) or 0
