"""Async service layer for book-related business logic."""

from models.entities import Book
from repositories.book_repository import BookRepository
from repositories.rental_repository import RentalRepository


class BookService:
    """Provides async book management operations."""

    def __init__(self, book_repo: BookRepository, rental_repo: RentalRepository):
        """Initialize the book service.

        Args:
            book_repo: Repository for book data access.
            rental_repo: Repository for rental data access.
        """
        self._book_repo = book_repo
        self._rental_repo = rental_repo

    async def search(self, query: str = "") -> list[Book]:
        """Search books by title, author, or ISBN.

        Args:
            query: Search string to filter books.

        Returns:
            A list of Book entities with relationships loaded.
        """
        return await self._book_repo.search(query)

    async def get_available(self) -> list[Book]:
        """Retrieve all books that are currently available for rental.

        Returns:
            A list of available Book entities.
        """
        return await self._book_repo.get_available()

    async def create(self, title: str, author: str = "", isbn: str = "", genre: str = "", storage_id: int | None = None, photo_path: str = "") -> None:
        """Create a new book in the library catalog.

        Args:
            title: Title of the book.
            author: Author of the book.
            isbn: International Standard Book Number.
            genre: Genre or category.
            storage_id: Optional storage location ID.
            photo_path: Path to the book's photo.
        """
        await self._book_repo.add(Book(title=title, author=author, isbn=isbn, genre=genre, storage_id=storage_id, photo_path=photo_path))

    async def update(self, book_id: int, title: str, author: str, isbn: str, genre: str, storage_id: int | None, photo_path: str = "") -> None:
        """Update an existing book's metadata.

        Args:
            book_id: The ID of the book to update.
            title: Updated title.
            author: Updated author.
            isbn: Updated ISBN.
            genre: Updated genre.
            storage_id: Updated storage location ID, or None.
            photo_path: Path to the book's photo.
        """
        book = Book(title=title, author=author, isbn=isbn, genre=genre, storage_id=storage_id, photo_path=photo_path)
        book.id = book_id
        await self._book_repo.update(book)

    async def delete(self, book_id: int) -> None:
        """Delete a book from the library catalog.

        Args:
            book_id: The ID of the book to delete.
        """
        await self._book_repo.delete(book_id)
