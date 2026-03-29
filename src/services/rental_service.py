"""Async service layer for rental transaction business logic."""

from models.entities import Rental
from repositories.rental_repository import RentalRepository
from repositories.book_repository import BookRepository


class RentalService:
    """Manages async book rental and return operations."""

    def __init__(self, rental_repo: RentalRepository, book_repo: BookRepository):
        """Initialize the rental service.

        Args:
            rental_repo: Repository for rental data access.
            book_repo: Repository for book data access.
        """
        self._rental_repo = rental_repo
        self._book_repo = book_repo

    async def get_active(self) -> list[Rental]:
        """Retrieve all currently active rentals.

        Returns:
            A list of active Rental entities.
        """
        return await self._rental_repo.get_active()

    async def get_all(self) -> list[Rental]:
        """Retrieve all rentals including returned ones.

        Returns:
            A list of all Rental entities.
        """
        return await self._rental_repo.get_all()

    async def rent_book(self, book_id: int, client_id: int, due_date: str) -> None:
        """Rent a book to a client.

        Args:
            book_id: The ID of the book to rent.
            client_id: The ID of the client renting the book.
            due_date: The due date for return in ISO format (YYYY-MM-DD).
        """
        await self._rental_repo.add(Rental(book_id=book_id, client_id=client_id, due_date=due_date))
        await self._book_repo.update_status(book_id, "rented")

    async def return_book(self, rental_id: int, return_storage_id: int) -> None:
        """Process a book return.

        Args:
            rental_id: The ID of the rental to close.
            return_storage_id: The ID of the storage where the book is returned.
        """
        book_id = await self._rental_repo.mark_returned(rental_id, return_storage_id)
        if book_id:
            await self._book_repo.update_status(book_id, "available", return_storage_id)
