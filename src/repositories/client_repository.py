"""Async repository for Client entity persistence and retrieval."""

from sqlalchemy import select, or_
from sqlalchemy.orm import subqueryload
from models.entities import Client, Rental
from repositories.base import BaseRepository


class ClientRepository(BaseRepository[Client]):
    """Handles all async database operations for Client entities."""

    async def get_all(self) -> list[Client]:
        """Retrieve all clients from the database.

        Returns:
            A list of all Client entities ordered by name.
        """
        return await self.search("")

    async def search(self, query: str) -> list[Client]:
        """Search clients by name, email, or phone.

        Args:
            query: Search string to match against name, email, and phone.
                An empty string returns all clients.

        Returns:
            A list of matching Client entities ordered by name.
        """
        async with self._session() as session:
            stmt = select(Client).options(subqueryload(Client.rentals)).order_by(Client.name)
            if query:
                like = f"%{query}%"
                stmt = stmt.where(
                    or_(Client.name.ilike(like), Client.email.ilike(like), Client.phone.ilike(like))
                )
            result = await session.scalars(stmt)
            results = list(result.all())
            return self._detach(session, results)

    async def add(self, entity: Client) -> None:
        """Insert a new client into the database.

        Args:
            entity: The Client to persist.
        """
        async with self._session() as session:
            session.add(entity)
            await session.commit()

    async def update(self, entity: Client) -> None:
        """Update an existing client's information.

        Args:
            entity: The Client with updated fields. Must have a valid id.
        """
        async with self._session() as session:
            client = await session.get(Client, entity.id)
            if client:
                client.name = entity.name
                client.email = entity.email
                client.phone = entity.phone
                client.address = entity.address
                client.photo_path = entity.photo_path
                await session.commit()

    async def delete(self, entity_id: int) -> None:
        """Delete a client from the database.

        Args:
            entity_id: The ID of the client to delete.
        """
        async with self._session() as session:
            client = await session.get(Client, entity_id)
            if client:
                await session.delete(client)
                await session.commit()
