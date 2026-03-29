"""Async integration tests for book CRUD and search operations."""

import pytest
from services.container import ServiceContainer


@pytest.mark.asyncio
class TestBookIntegration:
    """Tests for creating, reading, updating, searching, and deleting books."""

    async def test_create_book(self, container: ServiceContainer):
        """Creating a book should make it retrievable."""
        await container.books.create("Test Book", "Author", "123", "Fiction")
        books = await container.books.search()
        assert len(books) == 1
        assert books[0].title == "Test Book"
        assert books[0].author == "Author"
        assert books[0].status == "available"

    async def test_create_book_with_storage(self, container: ServiceContainer):
        """A book created with a storage should show the storage name."""
        await container.storages.create("Shelf A", "Room 1", 50)
        storage = (await container.storages.get_all())[0]
        await container.books.create("Test Book", storage_id=storage.id)
        book = (await container.books.search())[0]
        assert book.storage_name == "Shelf A"
        assert book.location_display == "Shelf A"

    async def test_update_book(self, container: ServiceContainer):
        """Updating a book should persist the new values."""
        await container.books.create("Old Title", "Old Author")
        book = (await container.books.search())[0]
        await container.books.update(book.id, "New Title", "New Author", "999", "Sci-Fi", None)
        updated = (await container.books.search())[0]
        assert updated.title == "New Title"
        assert updated.author == "New Author"
        assert updated.isbn == "999"
        assert updated.genre == "Sci-Fi"

    async def test_delete_book(self, container: ServiceContainer):
        """Deleting a book should remove it from search results."""
        await container.books.create("To Delete")
        book = (await container.books.search())[0]
        await container.books.delete(book.id)
        assert len(await container.books.search()) == 0

    async def test_search_by_title(self, container: ServiceContainer):
        """Search should match books by title substring."""
        await container.books.create("The Great Gatsby", "Fitzgerald")
        await container.books.create("Great Expectations", "Dickens")
        await container.books.create("1984", "Orwell")
        results = await container.books.search("great")
        assert len(results) == 2

    async def test_search_by_author(self, container: ServiceContainer):
        """Search should match books by author substring."""
        await container.books.create("Book A", "Jane Austen")
        await container.books.create("Book B", "Mark Twain")
        results = await container.books.search("austen")
        assert len(results) == 1
        assert results[0].author == "Jane Austen"

    async def test_search_by_isbn(self, container: ServiceContainer):
        """Search should match books by ISBN substring."""
        await container.books.create("Book A", isbn="978-123")
        await container.books.create("Book B", isbn="978-456")
        results = await container.books.search("456")
        assert len(results) == 1

    async def test_get_available_excludes_rented(self, container: ServiceContainer):
        """get_available should only return books with status 'available'."""
        await container.books.create("Available Book")
        await container.books.create("Rented Book")
        await container.clients.create("Client")
        book = (await container.books.search("Rented"))[0]
        client = (await container.clients.get_all())[0]
        await container.rentals.rent_book(book.id, client.id, "2099-12-31")
        available = await container.books.get_available()
        assert len(available) == 1
        assert available[0].title == "Available Book"

    async def test_book_is_available_property(self, container: ServiceContainer):
        """is_available should reflect the book status."""
        await container.books.create("Test")
        book = (await container.books.search())[0]
        assert book.is_available is True

    async def test_books_ordered_by_title(self, container: ServiceContainer):
        """Books should be returned in alphabetical order by title."""
        await container.books.create("Zebra")
        await container.books.create("Apple")
        await container.books.create("Mango")
        titles = [b.title for b in await container.books.search()]
        assert titles == ["Apple", "Mango", "Zebra"]
