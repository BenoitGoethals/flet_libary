"""Async service layer for client-related business logic."""

from models.entities import Client
from repositories.client_repository import ClientRepository
from repositories.rental_repository import RentalRepository


class ClientService:
    """Provides async client management operations."""

    def __init__(self, client_repo: ClientRepository, rental_repo: RentalRepository):
        self._client_repo = client_repo
        self._rental_repo = rental_repo

    async def search(self, query: str = "") -> list[Client]:
        return await self._client_repo.search(query)

    async def get_all(self) -> list[Client]:
        return await self._client_repo.get_all()

    async def create(self, name: str, email: str = "", phone: str = "", photo_path: str = "") -> None:
        await self._client_repo.add(Client(name=name, email=email, phone=phone, photo_path=photo_path))

    async def update(self, client_id: int, name: str, email: str, phone: str, photo_path: str = "") -> None:
        client = Client(name=name, email=email, phone=phone, photo_path=photo_path)
        client.id = client_id
        await self._client_repo.update(client)

    async def delete(self, client_id: int) -> None:
        await self._client_repo.delete(client_id)
