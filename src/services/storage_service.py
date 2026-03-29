"""Async service layer for storage location business logic."""

from dataclasses import dataclass
from models.entities import Storage
from repositories.storage_repository import StorageRepository


@dataclass
class StorageWithCount:
    """Storage data enriched with current book count for display purposes.

    Attributes:
        storage: The Storage ORM entity.
        book_count: Number of available books currently in this storage.
    """

    storage: Storage
    book_count: int

    @property
    def id(self) -> int:
        """Get the storage ID."""
        return self.storage.id

    @property
    def name(self) -> str:
        """Get the storage name."""
        return self.storage.name

    @property
    def location(self) -> str:
        """Get the storage location."""
        return self.storage.location or ""

    @property
    def capacity(self) -> int:
        """Get the storage capacity."""
        return self.storage.capacity or 0


class StorageService:
    """Provides async storage management operations with book count enrichment."""

    def __init__(self, repository: StorageRepository):
        """Initialize the storage service.

        Args:
            repository: Repository for storage data access.
        """
        self._repo = repository

    async def get_all(self) -> list[StorageWithCount]:
        """Retrieve all storages with their current book counts.

        Returns:
            A list of StorageWithCount instances.
        """
        storages = await self._repo.get_all()
        result = []
        for s in storages:
            count = await self._repo.get_book_count(s.id)
            result.append(StorageWithCount(storage=s, book_count=count))
        return result

    async def get_all_raw(self) -> list[Storage]:
        """Retrieve all storages as raw ORM entities (for dropdowns etc).

        Returns:
            A list of Storage entities.
        """
        return await self._repo.get_all()

    async def create(self, name: str, location: str = "", capacity: int = 0) -> None:
        """Create a new storage location.

        Args:
            name: Name of the storage.
            location: Physical location description.
            capacity: Maximum book capacity.
        """
        await self._repo.add(Storage(name=name, location=location, capacity=capacity))

    async def update(self, storage_id: int, name: str, location: str, capacity: int) -> None:
        """Update an existing storage location.

        Args:
            storage_id: The ID of the storage to update.
            name: Updated name.
            location: Updated location.
            capacity: Updated capacity.
        """
        s = Storage(name=name, location=location, capacity=capacity)
        s.id = storage_id
        await self._repo.update(s)

    async def delete(self, storage_id: int) -> None:
        """Delete a storage location.

        Args:
            storage_id: The ID of the storage to delete.
        """
        await self._repo.delete(storage_id)
