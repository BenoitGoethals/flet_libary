"""Async integration tests for client CRUD and search operations."""

import pytest
from services.container import ServiceContainer


@pytest.mark.asyncio
class TestClientIntegration:
    """Tests for creating, reading, updating, searching, and deleting clients."""

    async def test_create_client(self, container: ServiceContainer):
        """Creating a client should make them retrievable."""
        await container.clients.create("Alice", "alice@mail.com", "555-1234", "123 Main St")
        clients = await container.clients.search()
        assert len(clients) == 1
        assert clients[0].name == "Alice"
        assert clients[0].email == "alice@mail.com"
        assert clients[0].phone == "555-1234"

    async def test_update_client(self, container: ServiceContainer):
        """Updating a client should persist the new values."""
        await container.clients.create("Alice", "old@mail.com")
        client = (await container.clients.search())[0]
        await container.clients.update(client.id, "Alice Updated", "new@mail.com", "555-9999", "456 Oak Ave")
        updated = (await container.clients.search())[0]
        assert updated.name == "Alice Updated"
        assert updated.email == "new@mail.com"

    async def test_delete_client(self, container: ServiceContainer):
        """Deleting a client should remove them from the list."""
        await container.clients.create("Alice")
        client = (await container.clients.search())[0]
        await container.clients.delete(client.id)
        assert len(await container.clients.search()) == 0

    async def test_search_by_name(self, container: ServiceContainer):
        """Search should match clients by name substring."""
        await container.clients.create("Alice Johnson")
        await container.clients.create("Bob Smith")
        results = await container.clients.search("alice")
        assert len(results) == 1

    async def test_search_by_email(self, container: ServiceContainer):
        """Search should match clients by email substring."""
        await container.clients.create("Alice", "alice@special.com")
        await container.clients.create("Bob", "bob@other.com")
        results = await container.clients.search("special")
        assert len(results) == 1

    async def test_active_rental_count(self, container: ServiceContainer):
        """active_rental_count should reflect unreturned rentals."""
        await container.clients.create("Alice")
        await container.books.create("Book 1")
        await container.books.create("Book 2")
        client = (await container.clients.search())[0]
        books = await container.books.search()
        await container.rentals.rent_book(books[0].id, client.id, "2099-12-31")
        await container.rentals.rent_book(books[1].id, client.id, "2099-12-31")
        clients = await container.clients.search()
        assert clients[0].active_rental_count == 2

    async def test_clients_ordered_by_name(self, container: ServiceContainer):
        """Clients should be returned in alphabetical order by name."""
        await container.clients.create("Zara")
        await container.clients.create("Anna")
        await container.clients.create("Mike")
        names = [c.name for c in await container.clients.search()]
        assert names == ["Anna", "Mike", "Zara"]
