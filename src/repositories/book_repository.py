"""Async repository for Book entity persistence and retrieval."""

from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload, subqueryload
from models.entities import Book, Rental
from repositories.base import BaseRepository


class BookRepository(BaseRepository[Book]):
    """Handles all async database operations for Book entities."""

    async def get_all(self) -> list[Book]:
        """Retrieve all books from the database.

        Returns:
            A list of all Book entities with storage info populated.
        """
        return await self.search("")

    async def search(self, query: str) -> list[Book]:
        """Search books by title, author, or ISBN.

        Args:
            query: Search string to match against title, author, and ISBN.
                An empty string returns all books.

        Returns:
            A list of matching Book entities ordered by title.
        """
        async with self._session() as session:
            stmt = (
                select(Book)
                .options(
                    joinedload(Book.storage),
                    subqueryload(Book.rentals).joinedload(Rental.client),
                )
                .order_by(Book.title)
            )
            if query:
                like = f"%{query}%"
                stmt = stmt.where(
                    or_(Book.title.ilike(like), Book.author.ilike(like), Book.isbn.ilike(like))
                )
            result = await session.scalars(stmt)
            results = list(result.unique().all())
            return self._detach(session, results)

    async def get_available(self) -> list[Book]:
        """Retrieve all books with 'available' status.

        Returns:
            A list of available Book entities ordered by title.
        """
        async with self._session() as session:
            stmt = (
                select(Book)
                .options(joinedload(Book.storage))
                .where(Book.status == "available")
                .order_by(Book.title)
            )
            result = await session.scalars(stmt)
            results = list(result.unique().all())
            return self._detach(session, results)

    async def add(self, entity: Book) -> None:
        """Insert a new book into the database.

        Args:
            entity: The Book to persist. The id field is ignored.
        """
        async with self._session() as session:
            session.add(entity)
            await session.commit()

    async def update(self, entity: Book) -> None:
        """Update an existing book's metadata.

        Args:
            entity: The Book with updated fields. Must have a valid id.
        """
        async with self._session() as session:
            book = await session.get(Book, entity.id)
            if book:
                book.title = entity.title
                book.author = entity.author
                book.isbn = entity.isbn
                book.genre = entity.genre
                book.photo_path = entity.photo_path
                book.storage_id = entity.storage_id
                await session.commit()

    async def update_status(self, book_id: int, status: str, storage_id: int | None = None) -> None:
        """Update a book's status and optionally its storage assignment.

        Args:
            book_id: The ID of the book to update.
            status: The new status value ('available' or 'rented').
            storage_id: The storage ID to assign, or None to clear.
        """
        async with self._session() as session:
            book = await session.get(Book, book_id)
            if book:
                book.status = status
                book.storage_id = storage_id
                await session.commit()

    async def delete(self, entity_id: int) -> None:
        """Delete a book from the database.

        Args:
            entity_id: The ID of the book to delete.
        """
        async with self._session() as session:
            book = await session.get(Book, entity_id)
            if book:
                await session.delete(book)
                await session.commit()

    async def get_by_id(self, book_id: int) -> Book | None:
        """Retrieve a single book by its ID.

        Args:
            book_id: The ID of the book to fetch.

        Returns:
            The matching Book entity, or None if not found.
        """
        async with self._session() as session:
            stmt = (
                select(Book)
                .options(
                    joinedload(Book.storage),
                    subqueryload(Book.rentals).joinedload(Rental.client),
                )
                .where(Book.id == book_id)
            )
            result = await session.scalars(stmt)
            obj = result.unique().first()
            return self._detach_one(session, obj)
