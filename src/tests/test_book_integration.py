"""Integration tests for book CRUD and search operations."""

import pytest
from services.container import ServiceContainer


class TestBookIntegration:
    """Tests for creating, reading, updating, searching, and deleting books."""

    def test_create_book(self, container: ServiceContainer):
        """Creating a book should make it retrievable."""
        container.books.create("Test Book", "Author", "123", "Fiction")
        books = container.books.search()
        assert len(books) == 1
        assert books[0].title == "Test Book"
        assert books[0].author == "Author"
        assert books[0].status == "available"

    def test_create_book_with_storage(self, container: ServiceContainer):
        """A book created with a storage should show the storage name."""
        container.storages.create("Shelf A", "Room 1", 50)
        storage = container.storages.get_all()[0]
        container.books.create("Test Book", storage_id=storage.id)
        book = container.books.search()[0]
        assert book.storage_name == "Shelf A"
        assert book.location_display == "Shelf A"

    def test_update_book(self, container: ServiceContainer):
        """Updating a book should persist the new values."""
        container.books.create("Old Title", "Old Author")
        book = container.books.search()[0]
        container.books.update(book.id, "New Title", "New Author", "999", "Sci-Fi", None)
        updated = container.books.search()[0]
        assert updated.title == "New Title"
        assert updated.author == "New Author"
        assert updated.isbn == "999"
        assert updated.genre == "Sci-Fi"

    def test_delete_book(self, container: ServiceContainer):
        """Deleting a book should remove it from search results."""
        container.books.create("To Delete")
        book = container.books.search()[0]
        container.books.delete(book.id)
        assert len(container.books.search()) == 0

    def test_search_by_title(self, container: ServiceContainer):
        """Search should match books by title substring."""
        container.books.create("The Great Gatsby", "Fitzgerald")
        container.books.create("Great Expectations", "Dickens")
        container.books.create("1984", "Orwell")
        results = container.books.search("great")
        assert len(results) == 2

    def test_search_by_author(self, container: ServiceContainer):
        """Search should match books by author substring."""
        container.books.create("Book A", "Jane Austen")
        container.books.create("Book B", "Mark Twain")
        results = container.books.search("austen")
        assert len(results) == 1
        assert results[0].author == "Jane Austen"

    def test_search_by_isbn(self, container: ServiceContainer):
        """Search should match books by ISBN substring."""
        container.books.create("Book A", isbn="978-123")
        container.books.create("Book B", isbn="978-456")
        results = container.books.search("456")
        assert len(results) == 1

    def test_get_available_excludes_rented(self, container: ServiceContainer):
        """get_available should only return books with status 'available'."""
        container.books.create("Available Book")
        container.books.create("Rented Book")
        container.clients.create("Client")
        book = container.books.search("Rented")[0]
        client = container.clients.get_all()[0]
        container.rentals.rent_book(book.id, client.id, "2099-12-31")
        available = container.books.get_available()
        assert len(available) == 1
        assert available[0].title == "Available Book"

    def test_book_is_available_property(self, container: ServiceContainer):
        """is_available should reflect the book status."""
        container.books.create("Test")
        book = container.books.search()[0]
        assert book.is_available is True

    def test_books_ordered_by_title(self, container: ServiceContainer):
        """Books should be returned in alphabetical order by title."""
        container.books.create("Zebra")
        container.books.create("Apple")
        container.books.create("Mango")
        titles = [b.title for b in container.books.search()]
        assert titles == ["Apple", "Mango", "Zebra"]
