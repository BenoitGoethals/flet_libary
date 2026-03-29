"""Async integration tests for rental operations (rent, return, history)."""

import pytest
import pytest_asyncio
from datetime import date, timedelta
from services.container import ServiceContainer


@pytest.mark.asyncio
class TestRentalIntegration:
    """Tests for renting books, returning books, and rental queries."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_data(self, container: ServiceContainer):
        """Seed a storage, two books, and a client for each test."""
        self.container = container
        await container.storages.create("Main Shelf", "Room 1", 100)
        await container.books.create("Book A", "Author A", storage_id=1)
        await container.books.create("Book B", "Author B", storage_id=1)
        await container.clients.create("Alice", "alice@mail.com", "555-0001")

    async def test_rent_book(self):
        """Renting a book should change its status and create an active rental."""
        books = await self.container.books.search()
        client = (await self.container.clients.get_all())[0]
        due = (date.today() + timedelta(days=14)).isoformat()

        await self.container.rentals.rent_book(books[0].id, client.id, due)

        updated = (await self.container.books.search("Book A"))[0]
        assert updated.status == "rented"
        assert not updated.is_available

        active = await self.container.rentals.get_active()
        assert len(active) == 1
        assert active[0].book.title == "Book A"
        assert active[0].client.name == "Alice"
        assert active[0].due_date == due

    async def test_return_book(self):
        """Returning a book should close the rental and set status to available."""
        books = await self.container.books.search()
        client = (await self.container.clients.get_all())[0]
        storage = (await self.container.storages.get_all())[0]
        due = (date.today() + timedelta(days=14)).isoformat()

        await self.container.rentals.rent_book(books[0].id, client.id, due)
        rental = (await self.container.rentals.get_active())[0]
        await self.container.rentals.return_book(rental.id, storage.id)

        assert len(await self.container.rentals.get_active()) == 0

        book = (await self.container.books.search("Book A"))[0]
        assert book.status == "available"
        assert book.storage_id == storage.id

    async def test_return_to_different_storage(self):
        """A book can be returned to a different storage than it came from."""
        await self.container.storages.create("Backroom", "Room 2", 50)
        books = await self.container.books.search()
        client = (await self.container.clients.get_all())[0]
        storages = await self.container.storages.get_all()
        backroom = [s for s in storages if s.name == "Backroom"][0]

        await self.container.rentals.rent_book(books[0].id, client.id, "2099-12-31")
        rental = (await self.container.rentals.get_active())[0]
        await self.container.rentals.return_book(rental.id, backroom.id)

        book = (await self.container.books.search("Book A"))[0]
        assert book.storage_name == "Backroom"

    async def test_rental_history(self):
        """get_all should include both active and returned rentals."""
        books = await self.container.books.search()
        client = (await self.container.clients.get_all())[0]
        storage = (await self.container.storages.get_all())[0]

        await self.container.rentals.rent_book(books[0].id, client.id, "2099-12-31")
        await self.container.rentals.rent_book(books[1].id, client.id, "2099-12-31")

        rental = (await self.container.rentals.get_active())[0]
        await self.container.rentals.return_book(rental.id, storage.id)

        all_rentals = await self.container.rentals.get_all()
        assert len(all_rentals) == 2
        active = [r for r in all_rentals if r.is_active]
        returned = [r for r in all_rentals if not r.is_active]
        assert len(active) == 1
        assert len(returned) == 1

    async def test_overdue_rental(self):
        """A rental past its due date should be marked as overdue."""
        books = await self.container.books.search()
        client = (await self.container.clients.get_all())[0]
        past_date = (date.today() - timedelta(days=5)).isoformat()

        await self.container.rentals.rent_book(books[0].id, client.id, past_date)

        active = await self.container.rentals.get_active()
        assert len(active) == 1
        assert active[0].is_overdue is True

    async def test_future_rental_not_overdue(self):
        """A rental with a future due date should not be overdue."""
        books = await self.container.books.search()
        client = (await self.container.clients.get_all())[0]
        future_date = (date.today() + timedelta(days=30)).isoformat()

        await self.container.rentals.rent_book(books[0].id, client.id, future_date)

        active = await self.container.rentals.get_active()
        assert active[0].is_overdue is False

    async def test_book_location_display_when_rented(self):
        """A rented book's location_display should show the client name."""
        books = await self.container.books.search()
        client = (await self.container.clients.get_all())[0]

        await self.container.rentals.rent_book(books[0].id, client.id, "2099-12-31")

        book = (await self.container.books.search("Book A"))[0]
        assert "Alice" in book.location_display

    async def test_multiple_rentals_per_client(self):
        """A client can rent multiple books simultaneously."""
        books = await self.container.books.search()
        client = (await self.container.clients.get_all())[0]

        await self.container.rentals.rent_book(books[0].id, client.id, "2099-12-31")
        await self.container.rentals.rent_book(books[1].id, client.id, "2099-12-31")

        active = await self.container.rentals.get_active()
        assert len(active) == 2

        clients = await self.container.clients.search()
        assert clients[0].active_rental_count == 2
