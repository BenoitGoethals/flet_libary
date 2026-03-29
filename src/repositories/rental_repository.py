"""Async repository for Rental entity persistence and retrieval."""

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from models.entities import Rental
from repositories.base import BaseRepository


class RentalRepository(BaseRepository[Rental]):
    """Handles all async database operations for Rental entities."""

    async def get_all(self) -> list[Rental]:
        """Retrieve all rentals with associated book, client, and storage details.

        Returns:
            A list of all Rental entities ordered by rental date descending.
        """
        async with self._session() as session:
            stmt = (
                select(Rental)
                .options(
                    joinedload(Rental.book),
                    joinedload(Rental.client),
                    joinedload(Rental.return_storage),
                )
                .order_by(Rental.rented_at.desc())
            )
            result = await session.scalars(stmt)
            results = list(result.unique().all())
            return self._detach(session, results)

    async def get_active(self) -> list[Rental]:
        """Retrieve all active (unreturned) rentals.

        Returns:
            A list of active Rental entities ordered by due date.
        """
        async with self._session() as session:
            stmt = (
                select(Rental)
                .options(joinedload(Rental.book), joinedload(Rental.client))
                .where(Rental.returned_at.is_(None))
                .order_by(Rental.due_date)
            )
            result = await session.scalars(stmt)
            results = list(result.unique().all())
            return self._detach(session, results)

    async def get_by_client(self, client_id: int) -> list[Rental]:
        """Retrieve all rentals for a specific client.

        Args:
            client_id: The ID of the client.

        Returns:
            A list of Rental entities for the client.
        """
        async with self._session() as session:
            stmt = (
                select(Rental)
                .options(joinedload(Rental.book))
                .where(Rental.client_id == client_id)
                .order_by(Rental.rented_at.desc())
            )
            result = await session.scalars(stmt)
            results = list(result.unique().all())
            return self._detach(session, results)

    async def get_active_for_book(self, book_id: int) -> Rental | None:
        """Retrieve the active rental for a specific book, if any.

        Args:
            book_id: The ID of the book.

        Returns:
            The active Rental for the book, or None.
        """
        async with self._session() as session:
            stmt = (
                select(Rental)
                .options(joinedload(Rental.client))
                .where(Rental.book_id == book_id, Rental.returned_at.is_(None))
            )
            result = await session.scalars(stmt)
            obj = result.first()
            return self._detach_one(session, obj)

    async def add(self, entity: Rental) -> None:
        """Insert a new rental record into the database.

        Args:
            entity: The Rental to persist.
        """
        async with self._session() as session:
            session.add(entity)
            await session.commit()

    async def mark_returned(self, rental_id: int, return_storage_id: int) -> int | None:
        """Mark a rental as returned and record the return storage.

        Args:
            rental_id: The ID of the rental to mark as returned.
            return_storage_id: The ID of the storage where the book was returned.

        Returns:
            The book_id of the returned book, or None if not found.
        """
        async with self._session() as session:
            rental = await session.get(Rental, rental_id)
            if not rental:
                return None
            rental.returned_at = datetime.now().isoformat()
            rental.return_storage_id = return_storage_id
            book_id = rental.book_id
            await session.commit()
            return book_id

    async def update(self, entity: Rental) -> None:
        """Update a rental record (not implemented).

        Args:
            entity: The Rental entity to update.
        """
        pass

    async def delete(self, entity_id: int) -> None:
        """Delete a rental record from the database.

        Args:
            entity_id: The ID of the rental to delete.
        """
        async with self._session() as session:
            rental = await session.get(Rental, entity_id)
            if rental:
                await session.delete(rental)
                await session.commit()
