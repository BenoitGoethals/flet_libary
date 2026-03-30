"""Async repository for AppUser entity persistence and retrieval."""

from sqlalchemy import select, or_
from models.entities import AppUser
from repositories.base import BaseRepository


class UserRepository(BaseRepository[AppUser]):
    """Handles all async database operations for AppUser entities."""

    async def get_all(self) -> list[AppUser]:
        async with self._session() as session:
            result = await session.scalars(select(AppUser).order_by(AppUser.username))
            results = list(result.all())
            return self._detach(session, results)

    async def get_by_username(self, username: str) -> AppUser | None:
        async with self._session() as session:
            result = await session.scalars(
                select(AppUser).where(AppUser.username == username)
            )
            user = result.first()
            return self._detach_one(session, user)

    async def add(self, entity: AppUser) -> None:
        async with self._session() as session:
            session.add(entity)
            await session.commit()

    async def update(self, entity: AppUser) -> None:
        async with self._session() as session:
            user = await session.get(AppUser, entity.id)
            if user:
                user.username = entity.username
                user.display_name = entity.display_name
                user.email = entity.email
                user.role = entity.role
                if entity.password_hash:
                    user.password_hash = entity.password_hash
                await session.commit()

    async def delete(self, entity_id: int) -> None:
        async with self._session() as session:
            user = await session.get(AppUser, entity_id)
            if user:
                await session.delete(user)
                await session.commit()
