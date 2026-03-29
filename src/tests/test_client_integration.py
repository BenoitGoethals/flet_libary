"""Integration tests for client CRUD and search operations."""

import pytest
from services.container import ServiceContainer


class TestClientIntegration:
    """Tests for creating, reading, updating, searching, and deleting clients."""

    def test_create_client(self, container: ServiceContainer):
        """Creating a client should make them retrievable."""
        container.clients.create("Alice", "alice@mail.com", "555-1234", "123 Main St")
        clients = container.clients.search()
        assert len(clients) == 1
        assert clients[0].name == "Alice"
        assert clients[0].email == "alice@mail.com"
        assert clients[0].phone == "555-1234"

    def test_update_client(self, container: ServiceContainer):
        """Updating a client should persist the new values."""
        container.clients.create("Alice", "old@mail.com")
        client = container.clients.search()[0]
        container.clients.update(client.id, "Alice Updated", "new@mail.com", "555-9999", "456 Oak Ave")
        updated = container.clients.search()[0]
        assert updated.name == "Alice Updated"
        assert updated.email == "new@mail.com"

    def test_delete_client(self, container: ServiceContainer):
        """Deleting a client should remove them from the list."""
        container.clients.create("Alice")
        client = container.clients.search()[0]
        container.clients.delete(client.id)
        assert len(container.clients.search()) == 0

    def test_search_by_name(self, container: ServiceContainer):
        """Search should match clients by name substring."""
        container.clients.create("Alice Johnson")
        container.clients.create("Bob Smith")
        results = container.clients.search("alice")
        assert len(results) == 1

    def test_search_by_email(self, container: ServiceContainer):
        """Search should match clients by email substring."""
        container.clients.create("Alice", "alice@special.com")
        container.clients.create("Bob", "bob@other.com")
        results = container.clients.search("special")
        assert len(results) == 1

    def test_active_rental_count(self, container: ServiceContainer):
        """active_rental_count should reflect unreturned rentals."""
        container.clients.create("Alice")
        container.books.create("Book 1")
        container.books.create("Book 2")
        client = container.clients.search()[0]
        books = container.books.search()
        container.rentals.rent_book(books[0].id, client.id, "2099-12-31")
        container.rentals.rent_book(books[1].id, client.id, "2099-12-31")
        clients = container.clients.search()
        assert clients[0].active_rental_count == 2

    def test_clients_ordered_by_name(self, container: ServiceContainer):
        """Clients should be returned in alphabetical order by name."""
        container.clients.create("Zara")
        container.clients.create("Anna")
        container.clients.create("Mike")
        names = [c.name for c in container.clients.search()]
        assert names == ["Anna", "Mike", "Zara"]
