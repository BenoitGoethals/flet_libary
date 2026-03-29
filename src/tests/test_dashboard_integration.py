"""Integration tests for dashboard statistics."""

import pytest
from datetime import date, timedelta
from services.container import ServiceContainer


class TestDashboardIntegration:
    """Tests for dashboard stat aggregation."""

    def test_empty_dashboard(self, container: ServiceContainer):
        """An empty database should return all zeros."""
        stats = container.dashboard.get_stats()
        assert stats.total_books == 0
        assert stats.available == 0
        assert stats.rented == 0
        assert stats.total_clients == 0
        assert stats.active_rentals == 0
        assert stats.overdue == 0
        assert stats.total_storages == 0

    def test_counts_after_adding_data(self, container: ServiceContainer):
        """Stats should reflect added books, clients, and storages."""
        container.storages.create("S1")
        container.storages.create("S2")
        container.books.create("B1", storage_id=1)
        container.books.create("B2", storage_id=2)
        container.books.create("B3")
        container.clients.create("C1")

        stats = container.dashboard.get_stats()
        assert stats.total_books == 3
        assert stats.available == 3
        assert stats.rented == 0
        assert stats.total_clients == 1
        assert stats.total_storages == 2

    def test_rental_stats(self, container: ServiceContainer):
        """Renting a book should update rented count and active rentals."""
        container.storages.create("S1")
        container.books.create("B1", storage_id=1)
        container.books.create("B2", storage_id=1)
        container.clients.create("C1")

        client = container.clients.get_all()[0]
        books = container.books.search()
        container.rentals.rent_book(books[0].id, client.id, "2099-12-31")

        stats = container.dashboard.get_stats()
        assert stats.total_books == 2
        assert stats.available == 1
        assert stats.rented == 1
        assert stats.active_rentals == 1
        assert stats.overdue == 0

    def test_overdue_stats(self, container: ServiceContainer):
        """Overdue count should reflect rentals past due date."""
        container.storages.create("S1")
        container.books.create("B1", storage_id=1)
        container.books.create("B2", storage_id=1)
        container.clients.create("C1")

        client = container.clients.get_all()[0]
        books = container.books.search()
        past = (date.today() - timedelta(days=3)).isoformat()
        future = (date.today() + timedelta(days=10)).isoformat()
        container.rentals.rent_book(books[0].id, client.id, past)
        container.rentals.rent_book(books[1].id, client.id, future)

        stats = container.dashboard.get_stats()
        assert stats.active_rentals == 2
        assert stats.overdue == 1

    def test_return_updates_stats(self, container: ServiceContainer):
        """Returning a book should update available/rented/active counts."""
        container.storages.create("S1")
        container.books.create("B1", storage_id=1)
        container.clients.create("C1")

        client = container.clients.get_all()[0]
        book = container.books.search()[0]
        container.rentals.rent_book(book.id, client.id, "2099-12-31")

        rental = container.rentals.get_active()[0]
        storage = container.storages.get_all()[0]
        container.rentals.return_book(rental.id, storage.id)

        stats = container.dashboard.get_stats()
        assert stats.available == 1
        assert stats.rented == 0
        assert stats.active_rentals == 0
