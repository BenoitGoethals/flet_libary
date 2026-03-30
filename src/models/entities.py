"""SQLAlchemy ORM models representing the core domain entities of the library system."""

from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""
    pass


class AppUser(Base):
    """Represents an application user with role-based access."""

    __tablename__ = "app_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    display_name: Mapped[str] = mapped_column(String, default="")
    email: Mapped[Optional[str]] = mapped_column(String, default="")
    role: Mapped[str] = mapped_column(String, default="user")  # "admin" or "user"
    created_at: Mapped[Optional[str]] = mapped_column(String, server_default=func.now())

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


class Storage(Base):
    """Represents a physical storage location where books are kept.

    Attributes:
        id: Unique identifier for the storage.
        name: Display name of the storage location.
        location: Physical address or description.
        capacity: Maximum number of books the storage can hold.
        created_at: Timestamp of when the storage was created.
        books: Relationship to books assigned to this storage.
    """

    __tablename__ = "storages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String, default="")
    capacity: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[Optional[str]] = mapped_column(String, server_default=func.now())

    books: Mapped[List["Book"]] = relationship(back_populates="storage", passive_deletes=True)
    returned_rentals: Mapped[List["Rental"]] = relationship(
        back_populates="return_storage", foreign_keys="Rental.return_storage_id"
    )


class Book(Base):
    """Represents a book in the library catalog.

    Attributes:
        id: Unique identifier for the book.
        title: Title of the book.
        author: Author of the book.
        isbn: International Standard Book Number.
        genre: Genre or category of the book.
        storage_id: ID of the storage where the book is located.
        status: Current status ('available' or 'rented').
        created_at: Timestamp of when the book was added.
        storage: Relationship to the assigned Storage.
        rentals: Relationship to all Rental records for this book.
    """

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[Optional[str]] = mapped_column(String, default="")
    isbn: Mapped[Optional[str]] = mapped_column(String, default="")
    genre: Mapped[Optional[str]] = mapped_column(String, default="")
    photo_path: Mapped[Optional[str]] = mapped_column(String, default="")
    storage_id: Mapped[Optional[int]] = mapped_column(ForeignKey("storages.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String, default="available")
    created_at: Mapped[Optional[str]] = mapped_column(String, server_default=func.now())

    storage: Mapped[Optional["Storage"]] = relationship(back_populates="books")
    rentals: Mapped[List["Rental"]] = relationship(back_populates="book")

    @property
    def is_available(self) -> bool:
        """Check whether the book is currently available for rental.

        Returns:
            True if the book status is 'available', False otherwise.
        """
        return self.status == "available"

    @property
    def storage_name(self) -> str:
        """Get the name of the assigned storage.

        Returns:
            The storage name, or empty string if unassigned.
        """
        return self.storage.name if self.storage else ""

    @property
    def location_display(self) -> str:
        """Get a human-readable string describing the book's current location.

        Returns:
            A string showing the client name if rented, the storage name
            if assigned, or 'No storage' as a fallback.
        """
        if self.status == "rented":
            active = self.active_rental
            if active:
                return f"With: {active.client.name}"
        return self.storage_name or "No storage"

    @property
    def active_rental(self) -> Optional["Rental"]:
        """Get the currently active rental for this book, if any.

        Returns:
            The active Rental, or None.
        """
        for r in self.rentals:
            if r.returned_at is None:
                return r
        return None


class Client(Base):
    """Represents a library client who can rent books.

    Attributes:
        id: Unique identifier for the client.
        name: Full name of the client.
        email: Email address.
        phone: Phone number.
        created_at: Timestamp of when the client was registered.
        rentals: Relationship to all Rental records for this client.
    """

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, default="")
    phone: Mapped[Optional[str]] = mapped_column(String, default="")
    photo_path: Mapped[Optional[str]] = mapped_column(String, default="")
    created_at: Mapped[Optional[str]] = mapped_column(String, server_default=func.now())

    rentals: Mapped[List["Rental"]] = relationship(back_populates="client")

    @property
    def active_rental_count(self) -> int:
        """Count the number of currently active rentals for this client.

        Returns:
            The number of unreturned rentals.
        """
        return sum(1 for r in self.rentals if r.returned_at is None)


class Rental(Base):
    """Represents a book rental transaction between the library and a client.

    Attributes:
        id: Unique identifier for the rental.
        book_id: ID of the rented book.
        client_id: ID of the client who rented the book.
        rented_at: Timestamp of when the rental started.
        due_date: Date when the book is due for return.
        returned_at: Timestamp of when the book was returned, or None.
        return_storage_id: ID of the storage where the book was returned, or None.
        book: Relationship to the rented Book.
        client: Relationship to the renting Client.
        return_storage: Relationship to the return Storage.
    """

    __tablename__ = "rentals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    rented_at: Mapped[Optional[str]] = mapped_column(String, server_default=func.now())
    due_date: Mapped[Optional[str]] = mapped_column(String)
    returned_at: Mapped[Optional[str]] = mapped_column(String)
    return_storage_id: Mapped[Optional[int]] = mapped_column(ForeignKey("storages.id"))

    book: Mapped["Book"] = relationship(back_populates="rentals")
    client: Mapped["Client"] = relationship(back_populates="rentals")
    return_storage: Mapped[Optional["Storage"]] = relationship(back_populates="returned_rentals")

    @property
    def is_active(self) -> bool:
        """Check whether the rental is still active (book not yet returned).

        Returns:
            True if the book has not been returned, False otherwise.
        """
        return self.returned_at is None

    @property
    def is_overdue(self) -> bool:
        """Check whether the rental is overdue.

        Returns:
            True if the rental is active and the due date has passed.
        """
        return self.is_active and bool(self.due_date) and self.due_date < date.today().isoformat()

    @property
    def rented_date_short(self) -> str:
        """Get the rental start date truncated to YYYY-MM-DD format.

        Returns:
            The first 10 characters of the rented_at timestamp, or empty string.
        """
        return self.rented_at[:10] if self.rented_at else ""

    @property
    def returned_date_short(self) -> str:
        """Get the return date truncated to YYYY-MM-DD format.

        Returns:
            The first 10 characters of the returned_at timestamp, or empty string.
        """
        return self.returned_at[:10] if self.returned_at else ""


class DashboardStats:
    """Aggregated statistics for the library dashboard.

    Attributes:
        total_books: Total number of books in the library.
        available: Number of books currently available.
        rented: Number of books currently rented out.
        total_clients: Total number of registered clients.
        active_rentals: Number of rentals that have not been returned.
        overdue: Number of active rentals that are past their due date.
        total_storages: Total number of storage locations.
    """

    def __init__(
        self,
        total_books: int = 0,
        available: int = 0,
        rented: int = 0,
        total_clients: int = 0,
        active_rentals: int = 0,
        overdue: int = 0,
        total_storages: int = 0,
    ):
        self.total_books = total_books
        self.available = available
        self.rented = rented
        self.total_clients = total_clients
        self.active_rentals = active_rentals
        self.overdue = overdue
        self.total_storages = total_storages
