"""Dependency injection container wiring all repositories and services."""

from models.database import Database
from repositories.book_repository import BookRepository
from repositories.client_repository import ClientRepository
from repositories.storage_repository import StorageRepository
from repositories.rental_repository import RentalRepository
from repositories.user_repository import UserRepository
from services.book_service import BookService
from services.client_service import ClientService
from services.storage_service import StorageService
from services.rental_service import RentalService
from services.dashboard_service import DashboardService
from services.settings_service import SettingsService
from services.user_service import UserService
from services.mail_service import MailService


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
        self.user_repo = UserRepository(self._db)

        # Services
        self.books = BookService(self.book_repo, self.rental_repo)
        self.clients = ClientService(self.client_repo, self.rental_repo)
        self.storages = StorageService(self.storage_repo)
        self.mail = MailService()
        self.rentals = RentalService(self.rental_repo, self.book_repo, self.mail)
        self.dashboard = DashboardService(self._db)
        self.settings = SettingsService()
        self.users = UserService(self.user_repo)

    async def init(self):
        """Initialize the database schema and ensure a default admin exists."""
        await self._db.init_schema()
        # Seed default admin if no users exist yet
        existing = await self.users.get_all()
        if not existing:
            await self.users.create("admin", "admin", "Administrator", "admin", "admin@library.local")

    @property
    def database(self) -> Database:
        """Access the underlying Database instance.

        Returns:
            The Database instance used by this container.
        """
        return self._db
