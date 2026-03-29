"""Dependency injection container wiring all repositories and services."""

from models.database import Database
from repositories.book_repository import BookRepository
from repositories.client_repository import ClientRepository
from repositories.storage_repository import StorageRepository
from repositories.rental_repository import RentalRepository
from services.book_service import BookService
from services.client_service import ClientService
from services.storage_service import StorageService
from services.rental_service import RentalService
from services.dashboard_service import DashboardService


class ServiceContainer:
    """Simple DI container — single place to wire all dependencies."""

    def __init__(self, database: Database | None = None, db_url: str | None = None):
        """Initialize the container, creating all repositories and services.

        Note: Call `await container.init()` after construction to initialize the schema.

        Args:
            database: Optional Database instance. Takes priority over db_url.
            db_url: Optional database URL. If neither is provided, uses the singleton.
        """
        if database:
            self._db = database
        elif db_url:
            self._db = Database(db_url)
        else:
            self._db = Database.instance()

        # Repositories
        self.book_repo = BookRepository(self._db)
        self.client_repo = ClientRepository(self._db)
        self.storage_repo = StorageRepository(self._db)
        self.rental_repo = RentalRepository(self._db)

        # Services
        self.books = BookService(self.book_repo, self.rental_repo)
        self.clients = ClientService(self.client_repo, self.rental_repo)
        self.storages = StorageService(self.storage_repo)
        self.rentals = RentalService(self.rental_repo, self.book_repo)
        self.dashboard = DashboardService(self._db)

    async def init(self):
        """Initialize the database schema. Must be called after construction."""
        await self._db.init_schema()

    @property
    def database(self) -> Database:
        """Access the underlying Database instance.

        Returns:
            The Database instance used by this container.
        """
        return self._db
