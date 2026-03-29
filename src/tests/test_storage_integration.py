"""Integration tests for storage CRUD operations."""

import pytest
from services.container import ServiceContainer


class TestStorageIntegration:
    """Tests for creating, reading, updating, and deleting storages."""

    def test_create_storage(self, container: ServiceContainer):
        """Creating a storage should make it retrievable."""
        container.storages.create("Shelf A", "Room 1", 50)
        storages = container.storages.get_all()
        assert len(storages) == 1
        assert storages[0].name == "Shelf A"
        assert storages[0].location == "Room 1"
        assert storages[0].capacity == 50

    def test_update_storage(self, container: ServiceContainer):
        """Updating a storage should persist the new values."""
        container.storages.create("Shelf A", "Room 1", 50)
        storage = container.storages.get_all()[0]
        container.storages.update(storage.id, "Shelf B", "Room 2", 100)
        updated = container.storages.get_all()[0]
        assert updated.name == "Shelf B"
        assert updated.location == "Room 2"
        assert updated.capacity == 100

    def test_delete_storage(self, container: ServiceContainer):
        """Deleting a storage should remove it from the list."""
        container.storages.create("Shelf A", "Room 1", 50)
        storage = container.storages.get_all()[0]
        container.storages.delete(storage.id)
        assert len(container.storages.get_all()) == 0

    def test_storage_book_count(self, container: ServiceContainer):
        """Book count should reflect available books in the storage."""
        container.storages.create("Shelf A", "Room 1", 50)
        storage = container.storages.get_all()[0]
        container.books.create("Book 1", storage_id=storage.id)
        container.books.create("Book 2", storage_id=storage.id)
        storages = container.storages.get_all()
        assert storages[0].book_count == 2

    def test_multiple_storages_ordered_by_name(self, container: ServiceContainer):
        """Storages should be returned in alphabetical order."""
        container.storages.create("Zeta", "Z", 10)
        container.storages.create("Alpha", "A", 20)
        container.storages.create("Middle", "M", 30)
        names = [s.name for s in container.storages.get_all()]
        assert names == ["Alpha", "Middle", "Zeta"]
