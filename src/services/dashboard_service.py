"""Async service layer for aggregating dashboard statistics."""

from datetime import date
from sqlalchemy import select, func
from models.entities import DashboardStats, Book, Client, Rental, Storage
from models.database import Database


class DashboardService:
    """Provides async aggregated library statistics for the dashboard view."""

    def __init__(self, database: Database):
        """Initialize the dashboard service.

        Args:
            database: The Database instance for running aggregate queries.
        """
        self._db = database

    async def get_stats(self) -> DashboardStats:
        """Compute and return all dashboard statistics.

        Returns:
            A DashboardStats instance with all aggregate counts populated.
        """
        async with self._db.create_session() as session:
            return DashboardStats(
                total_books=await self._count(session, Book),
                available=await self._count(session, Book, Book.status == "available"),
                rented=await self._count(session, Book, Book.status == "rented"),
                total_clients=await self._count(session, Client),
                active_rentals=await self._count(session, Rental, Rental.returned_at.is_(None)),
                overdue=await self._count(
                    session, Rental,
                    Rental.returned_at.is_(None),
                    Rental.due_date < date.today().isoformat(),
                ),
                total_storages=await self._count(session, Storage),
            )

    @staticmethod
    async def _count(session, model, *filters) -> int:
        """Execute a COUNT query and return the scalar result.

        Args:
            session: An active async SQLAlchemy session.
            model: The ORM model class to count.
            *filters: Optional filter conditions.

        Returns:
            The integer count result.
        """
        stmt = select(func.count()).select_from(model)
        for f in filters:
            stmt = stmt.where(f)
        return await session.scalar(stmt) or 0
