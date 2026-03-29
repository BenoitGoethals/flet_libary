"""Async service layer for client-related business logic."""

from models.entities import Client
from repositories.client_repository import ClientRepository
from repositories.rental_repository import RentalRepository


class ClientService:
    """Provides async client management operations."""

    def __init__(self, client_repo: ClientRepository, rental_repo: RentalRepository):
        """Initialize the client service.

        Args:
            client_repo: Repository for client data access.
            rental_repo: Repository for rental data access.
        """
        self._client_repo = client_repo
        self._rental_repo = rental_repo

    async def search(self, query: str = "") -> list[Client]:
        """Search clients by name, email, or phone.

        Args:
            query: Search string to filter clients.

        Returns:
            A list of Client entities.
        """
        return await self._client_repo.search(query)

    async def get_all(self) -> list[Client]:
        """Retrieve all clients.

        Returns:
            A list of all Client entities.
        """
        return await self._client_repo.get_all()

    async def create(self, name: str, email: str = "", phone: str = "", address: str = "", photo_path: str = "") -> None:
        """Register a new client.

        Args:
            name: Full name of the client.
            email: Email address.
            phone: Phone number.
            address: Physical address.
            photo_path: Path to the client's photo.
        """
        await self._client_repo.add(Client(name=name, email=email, phone=phone, address=address, photo_path=photo_path))

    async def update(self, client_id: int, name: str, email: str, phone: str, address: str, photo_path: str = "") -> None:
        """Update an existing client's information.

        Args:
            client_id: The ID of the client to update.
            name: Updated name.
            email: Updated email.
            phone: Updated phone.
            address: Updated address.
            photo_path: Path to the client's photo.
        """
        client = Client(name=name, email=email, phone=phone, address=address, photo_path=photo_path)
        client.id = client_id
        await self._client_repo.update(client)

    async def delete(self, client_id: int) -> None:
        """Delete a client.

        Args:
            client_id: The ID of the client to delete.
        """
        await self._client_repo.delete(client_id)
