"""Async service layer for rental transaction business logic."""

from models.entities import Rental
from repositories.rental_repository import RentalRepository
from repositories.book_repository import BookRepository
from services.mail_service import MailService


class RentalService:
    """Manages async book rental and return operations."""

    def __init__(self, rental_repo: RentalRepository, book_repo: BookRepository,
                 mail_service: MailService | None = None):
        self._rental_repo = rental_repo
        self._book_repo = book_repo
        self._mail = mail_service

    async def get_active(self) -> list[Rental]:
        return await self._rental_repo.get_active()

    async def get_all(self) -> list[Rental]:
        return await self._rental_repo.get_all()

    async def rent_book(self, book_id: int, client_id: int, due_date: str) -> None:
        await self._rental_repo.add(Rental(book_id=book_id, client_id=client_id, due_date=due_date))
        await self._book_repo.update_status(book_id, "rented")

        # Send confirmation email
        if self._mail:
            rentals = await self._rental_repo.get_active()
            for r in rentals:
                if r.book_id == book_id and r.client_id == client_id and r.returned_at is None:
                    if r.client.email:
                        await self._mail.send_rental_confirmation(
                            r.client.name, r.client.email, r.book.title, due_date)
                    break

    async def return_book(self, rental_id: int, return_storage_id: int) -> None:
        # Grab rental info before marking returned (for the email)
        rentals = await self._rental_repo.get_active()
        rental_info = None
        for r in rentals:
            if r.id == rental_id:
                rental_info = r
                break

        book_id = await self._rental_repo.mark_returned(rental_id, return_storage_id)
        if book_id:
            await self._book_repo.update_status(book_id, "available", return_storage_id)

        # Send return confirmation email
        if self._mail and rental_info and rental_info.client.email:
            await self._mail.send_return_confirmation(
                rental_info.client.name, rental_info.client.email,
                rental_info.book.title)
