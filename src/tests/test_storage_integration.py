"""Async integration tests for storage CRUD operations."""

import pytest
from services.container import ServiceContainer


@pytest.mark.asyncio
class TestStorageIntegration:
    """Tests for creating, reading, updating, and deleting storages."""

    async def test_create_storage(self, container: ServiceContainer):
        """Creating a storage should make it retrievable."""
        await container.storages.create("Shelf A", "Room 1", 50)
        storages = await container.storages.get_all()
        assert len(storages) == 1
        assert storages[0].name == "Shelf A"
        assert storages[0].location == "Room 1"
        assert storages[0].capacity == 50

    async def test_update_storage(self, container: ServiceContainer):
        """Updating a storage should persist the new values."""
        await container.storages.create("Shelf A", "Room 1", 50)
        storage = (await container.storages.get_all())[0]
        await container.storages.update(storage.id, "Shelf B", "Room 2", 100)
        updated = (await container.storages.get_all())[0]
        assert updated.name == "Shelf B"
        assert updated.location == "Room 2"
        assert updated.capacity == 100

    async def test_delete_storage(self, container: ServiceContainer):
        """Deleting a storage should remove it from the list."""
        await container.storages.create("Shelf A", "Room 1", 50)
        storage = (await container.storages.get_all())[0]
        await container.storages.delete(storage.id)
        assert len(await container.storages.get_all()) == 0

    async def test_storage_book_count(self, container: ServiceContainer):
        """Book count should reflect available books in the storage."""
        await container.storages.create("Shelf A", "Room 1", 50)
        storage = (await container.storages.get_all())[0]
        await container.books.create("Book 1", storage_id=storage.id)
        await container.books.create("Book 2", storage_id=storage.id)
        storages = await container.storages.get_all()
        assert storages[0].book_count == 2

    async def test_multiple_storages_ordered_by_name(self, container: ServiceContainer):
        """Storages should be returned in alphabetical order."""
        await container.storages.create("Zeta", "Z", 10)
        await container.storages.create("Alpha", "A", 20)
        await container.storages.create("Middle", "M", 30)
        names = [s.name for s in await container.storages.get_all()]
        assert names == ["Alpha", "Middle", "Zeta"]
