"""Database configuration section components for the settings view.

Each section is responsible for rendering its own fields and
serializing/deserializing its configuration to/from a dictionary.
New database backends can be added by subclassing DatabaseSection.
"""

import flet as ft
from abc import ABC, abstractmethod


class DatabaseSection(ABC):
    """Abstract base for a database-type configuration section.

    Subclasses render their own fields and convert between UI ↔ dict.
    """

    @property
    @abstractmethod
    def key(self) -> str:
        """Unique key identifying this database type (e.g. 'sqlite')."""
        ...

    @property
    @abstractmethod
    def label(self) -> str:
        """Human-readable label shown on the toggle button."""
        ...

    @abstractmethod
    def build(self, cfg: dict) -> ft.Control:
        """Build the section's UI from a config dict.

        Args:
            cfg: The config sub-dict for this database type.

        Returns:
            A Flet control containing all fields.
        """
        ...

    @abstractmethod
    def to_dict(self) -> dict:
        """Serialize current field values to a config dict.

        Returns:
            The config sub-dict for this database type.
        """
        ...


class SqliteSection(DatabaseSection):
    """Configuration section for SQLite databases."""

    key = "sqlite"
    label = "SQLite"

    def build(self, cfg: dict) -> ft.Control:
        """Build SQLite configuration fields."""
        self._path = ft.TextField(
            label="Database file path",
            value=cfg.get("path", ""),
            expand=True,
        )
        self._control = ft.Column(
            [ft.Text("SQLite Settings", weight=ft.FontWeight.BOLD, size=16),
             self._path],
            spacing=10,
        )
        return self._control

    def to_dict(self) -> dict:
        """Return SQLite config from field values."""
        return {"path": self._path.value.strip()}


class MssqlSection(DatabaseSection):
    """Configuration section for MSSQL databases."""

    key = "mssql"
    label = "MSSQL"

    def build(self, cfg: dict) -> ft.Control:
        """Build MSSQL configuration fields."""
        self._host = ft.TextField(label="Host", value=cfg.get("host", "localhost"), expand=True)
        self._port = ft.TextField(
            label="Port", value=str(cfg.get("port", 1433)),
            width=100, keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._database = ft.TextField(label="Database", value=cfg.get("database", ""), expand=True)
        self._username = ft.TextField(label="Username", value=cfg.get("username", ""), expand=True)
        self._password = ft.TextField(
            label="Password", value=cfg.get("password", ""),
            password=True, can_reveal_password=True, expand=True,
        )
        self._driver = ft.TextField(
            label="ODBC Driver",
            value=cfg.get("driver", "ODBC Driver 18 for SQL Server"),
            expand=True,
        )
        self._control = ft.Column(
            [ft.Text("MSSQL Settings", weight=ft.FontWeight.BOLD, size=16),
             ft.Row([self._host, self._port], spacing=10),
             self._database,
             ft.Row([self._username, self._password], spacing=10),
             self._driver],
            spacing=10,
        )
        return self._control

    def to_dict(self) -> dict:
        """Return MSSQL config from field values."""
        port = int(self._port.value) if self._port.value.isdigit() else 1433
        return {
            "host": self._host.value.strip(),
            "port": port,
            "database": self._database.value.strip(),
            "username": self._username.value.strip(),
            "password": self._password.value,
            "driver": self._driver.value.strip(),
        }


class MariadbSection(DatabaseSection):
    """Configuration section for MariaDB databases."""

    key = "mariadb"
    label = "MariaDB"

    def build(self, cfg: dict) -> ft.Control:
        """Build MariaDB configuration fields."""
        self._host = ft.TextField(label="Host", value=cfg.get("host", "localhost"), expand=True)
        self._port = ft.TextField(
            label="Port", value=str(cfg.get("port", 3306)),
            width=100, keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._database = ft.TextField(label="Database", value=cfg.get("database", ""), expand=True)
        self._username = ft.TextField(label="Username", value=cfg.get("username", ""), expand=True)
        self._password = ft.TextField(
            label="Password", value=cfg.get("password", ""),
            password=True, can_reveal_password=True, expand=True,
        )
        self._charset = ft.TextField(
            label="Charset", value=cfg.get("charset", "utf8mb4"), expand=True,
        )
        self._control = ft.Column(
            [ft.Text("MariaDB Settings", weight=ft.FontWeight.BOLD, size=16),
             ft.Row([self._host, self._port], spacing=10),
             self._database,
             ft.Row([self._username, self._password], spacing=10),
             self._charset],
            spacing=10,
        )
        return self._control

    def to_dict(self) -> dict:
        """Return MariaDB config from field values."""
        port = int(self._port.value) if self._port.value.isdigit() else 3306
        return {
            "host": self._host.value.strip(),
            "port": port,
            "database": self._database.value.strip(),
            "username": self._username.value.strip(),
            "password": self._password.value,
            "charset": self._charset.value.strip(),
        }
