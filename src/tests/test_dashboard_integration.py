"""Async integration tests for dashboard statistics."""

import pytest
from datetime import date, timedelta
from services.container import ServiceContainer


@pytest.mark.asyncio
class TestDashboardIntegration:
    """Tests for dashboard stat aggregation."""

    async def test_empty_dashboard(self, container: ServiceContainer):
        """An empty database should return all zeros."""
        stats = await container.dashboard.get_stats()
        assert stats.total_books == 0
        assert stats.available == 0
        assert stats.rented == 0
        assert stats.total_clients == 0
        assert stats.active_rentals == 0
        assert stats.overdue == 0
        assert stats.total_storages == 0

    async def test_counts_after_adding_data(self, container: ServiceContainer):
        """Stats should reflect added books, clients, and storages."""
        await container.storages.create("S1")
        await container.storages.create("S2")
        await container.books.create("B1", storage_id=1)
        await container.books.create("B2", storage_id=2)
        await container.books.create("B3")
        await container.clients.create("C1")

        stats = await container.dashboard.get_stats()
        assert stats.total_books == 3
        assert stats.available == 3
        assert stats.rented == 0
        assert stats.total_clients == 1
        assert stats.total_storages == 2

    async def test_rental_stats(self, container: ServiceContainer):
        """Renting a book should update rented count and active rentals."""
        await container.storages.create("S1")
        await container.books.create("B1", storage_id=1)
        await container.books.create("B2", storage_id=1)
        await container.clients.create("C1")

        client = (await container.clients.get_all())[0]
        books = await container.books.search()
        await container.rentals.rent_book(books[0].id, client.id, "2099-12-31")

        stats = await container.dashboard.get_stats()
        assert stats.total_books == 2
        assert stats.available == 1
        assert stats.rented == 1
        assert stats.active_rentals == 1
        assert stats.overdue == 0

    async def test_overdue_stats(self, container: ServiceContainer):
        """Overdue count should reflect rentals past due date."""
        await container.storages.create("S1")
        await container.books.create("B1", storage_id=1)
        await container.books.create("B2", storage_id=1)
        await container.clients.create("C1")

        client = (await container.clients.get_all())[0]
        books = await container.books.search()
        past = (date.today() - timedelta(days=3)).isoformat()
        future = (date.today() + timedelta(days=10)).isoformat()
        await container.rentals.rent_book(books[0].id, client.id, past)
        await container.rentals.rent_book(books[1].id, client.id, future)

        stats = await container.dashboard.get_stats()
        assert stats.active_rentals == 2
        assert stats.overdue == 1

    async def test_return_updates_stats(self, container: ServiceContainer):
        """Returning a book should update available/rented/active counts."""
        await container.storages.create("S1")
        await container.books.create("B1", storage_id=1)
        await container.clients.create("C1")

        client = (await container.clients.get_all())[0]
        book = (await container.books.search())[0]
        await container.rentals.rent_book(book.id, client.id, "2099-12-31")

        rental = (await container.rentals.get_active())[0]
        storage = (await container.storages.get_all())[0]
        await container.rentals.return_book(rental.id, storage.id)

        stats = await container.dashboard.get_stats()
        assert stats.available == 1
        assert stats.rented == 0
        assert stats.active_rentals == 0
