"""Integration tests for rental operations (rent, return, history)."""

import pytest
from datetime import date, timedelta
from services.container import ServiceContainer


class TestRentalIntegration:
    """Tests for renting books, returning books, and rental queries."""

    @pytest.fixture(autouse=True)
    def setup_data(self, container: ServiceContainer):
        """Seed a storage, two books, and a client for each test."""
        self.container = container
        container.storages.create("Main Shelf", "Room 1", 100)
        container.books.create("Book A", "Author A", storage_id=1)
        container.books.create("Book B", "Author B", storage_id=1)
        container.clients.create("Alice", "alice@mail.com", "555-0001")

    def test_rent_book(self):
        """Renting a book should change its status and create an active rental."""
        books = self.container.books.search()
        client = self.container.clients.get_all()[0]
        due = (date.today() + timedelta(days=14)).isoformat()

        self.container.rentals.rent_book(books[0].id, client.id, due)

        updated = self.container.books.search("Book A")[0]
        assert updated.status == "rented"
        assert not updated.is_available

        active = self.container.rentals.get_active()
        assert len(active) == 1
        assert active[0].book.title == "Book A"
        assert active[0].client.name == "Alice"
        assert active[0].due_date == due

    def test_return_book(self):
        """Returning a book should close the rental and set status to available."""
        books = self.container.books.search()
        client = self.container.clients.get_all()[0]
        storage = self.container.storages.get_all()[0]
        due = (date.today() + timedelta(days=14)).isoformat()

        self.container.rentals.rent_book(books[0].id, client.id, due)
        rental = self.container.rentals.get_active()[0]
        self.container.rentals.return_book(rental.id, storage.id)

        assert len(self.container.rentals.get_active()) == 0

        book = self.container.books.search("Book A")[0]
        assert book.status == "available"
        assert book.storage_id == storage.id

    def test_return_to_different_storage(self):
        """A book can be returned to a different storage than it came from."""
        self.container.storages.create("Backroom", "Room 2", 50)
        books = self.container.books.search()
        client = self.container.clients.get_all()[0]
        storages = self.container.storages.get_all()
        backroom = [s for s in storages if s.name == "Backroom"][0]

        self.container.rentals.rent_book(books[0].id, client.id, "2099-12-31")
        rental = self.container.rentals.get_active()[0]
        self.container.rentals.return_book(rental.id, backroom.id)

        book = self.container.books.search("Book A")[0]
        assert book.storage_name == "Backroom"

    def test_rental_history(self):
        """get_all should include both active and returned rentals."""
        books = self.container.books.search()
        client = self.container.clients.get_all()[0]
        storage = self.container.storages.get_all()[0]

        self.container.rentals.rent_book(books[0].id, client.id, "2099-12-31")
        self.container.rentals.rent_book(books[1].id, client.id, "2099-12-31")

        rental = self.container.rentals.get_active()[0]
        self.container.rentals.return_book(rental.id, storage.id)

        all_rentals = self.container.rentals.get_all()
        assert len(all_rentals) == 2
        active = [r for r in all_rentals if r.is_active]
        returned = [r for r in all_rentals if not r.is_active]
        assert len(active) == 1
        assert len(returned) == 1

    def test_overdue_rental(self):
        """A rental past its due date should be marked as overdue."""
        books = self.container.books.search()
        client = self.container.clients.get_all()[0]
        past_date = (date.today() - timedelta(days=5)).isoformat()

        self.container.rentals.rent_book(books[0].id, client.id, past_date)

        active = self.container.rentals.get_active()
        assert len(active) == 1
        assert active[0].is_overdue is True

    def test_future_rental_not_overdue(self):
        """A rental with a future due date should not be overdue."""
        books = self.container.books.search()
        client = self.container.clients.get_all()[0]
        future_date = (date.today() + timedelta(days=30)).isoformat()

        self.container.rentals.rent_book(books[0].id, client.id, future_date)

        active = self.container.rentals.get_active()
        assert active[0].is_overdue is False

    def test_book_location_display_when_rented(self):
        """A rented book's location_display should show the client name."""
        books = self.container.books.search()
        client = self.container.clients.get_all()[0]

        self.container.rentals.rent_book(books[0].id, client.id, "2099-12-31")

        book = self.container.books.search("Book A")[0]
        assert "Alice" in book.location_display

    def test_multiple_rentals_per_client(self):
        """A client can rent multiple books simultaneously."""
        books = self.container.books.search()
        client = self.container.clients.get_all()[0]

        self.container.rentals.rent_book(books[0].id, client.id, "2099-12-31")
        self.container.rentals.rent_book(books[1].id, client.id, "2099-12-31")

        active = self.container.rentals.get_active()
        assert len(active) == 2

        clients = self.container.clients.search()
        assert clients[0].active_rental_count == 2
