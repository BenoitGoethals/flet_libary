"""Async service layer for user authentication and management."""

import hashlib
from models.entities import AppUser
from repositories.user_repository import UserRepository


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class UserService:
    """Provides async user management and authentication."""

    def __init__(self, user_repo: UserRepository):
        self._repo = user_repo

    async def authenticate(self, username: str, password: str) -> AppUser | None:
        user = await self._repo.get_by_username(username)
        if user and user.password_hash == _hash_password(password):
            return user
        return None

    async def get_all(self) -> list[AppUser]:
        return await self._repo.get_all()

    async def create(self, username: str, password: str, display_name: str = "",
                     role: str = "user", email: str = "") -> None:
        await self._repo.add(AppUser(
            username=username,
            password_hash=_hash_password(password),
            display_name=display_name,
            email=email,
            role=role,
        ))

    async def update(self, user_id: int, username: str, display_name: str, role: str,
                     password: str = "", email: str = "") -> None:
        user = AppUser(username=username, display_name=display_name, role=role,
                       email=email,
                       password_hash=_hash_password(password) if password else "")
        user.id = user_id
        await self._repo.update(user)

    async def delete(self, user_id: int) -> None:
        await self._repo.delete(user_id)
