"""Application configuration backed by a YAML settings file.

Loads database connection settings from ``settings.yml`` in the project
root.  If the file does not exist a default SQLite configuration is
written automatically.

The active database URL is assembled from the YAML values and exposed as
``DATABASE_URL`` for the rest of the application.
"""

import os
import yaml

SETTINGS_PATH: str = os.path.join(os.path.dirname(__file__), "settings.yml")

_DEFAULT_SETTINGS: dict = {
    "database": {
        "type": "sqlite",
        "sqlite": {
            "path": os.path.join(os.path.dirname(__file__), "library.db"),
        },
        "mssql": {
            "host": "localhost",
            "port": 1433,
            "database": "library",
            "username": "",
            "password": "",
            "driver": "ODBC Driver 18 for SQL Server",
        },
        "mariadb": {
            "host": "localhost",
            "port": 3306,
            "database": "library",
            "username": "",
            "password": "",
            "charset": "utf8mb4",
        },
    },
}


def load_settings() -> dict:
    """Load settings from the YAML file, creating defaults if missing.

    Returns:
        The parsed settings dictionary.
    """
    if not os.path.exists(SETTINGS_PATH):
        save_settings(_DEFAULT_SETTINGS)
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_settings(settings: dict) -> None:
    """Write settings to the YAML file.

    Args:
        settings: The settings dictionary to persist.
    """
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        yaml.dump(settings, f, default_flow_style=False, sort_keys=False)


def build_database_url(settings: dict) -> str:
    """Build an async SQLAlchemy URL from the settings dict.

    Args:
        settings: The full settings dictionary.

    Returns:
        An async database URL string.
    """
    db = settings["database"]
    db_type = db["type"]
    if db_type == "mssql":
        m = db["mssql"]
        driver = m.get("driver", "ODBC Driver 18 for SQL Server").replace(" ", "+")
        return (
            f"mssql+aioodbc://{m['username']}:{m['password']}"
            f"@{m['host']}:{m.get('port', 1433)}/{m['database']}"
            f"?driver={driver}"
        )
    if db_type == "mariadb":
        m = db["mariadb"]
        charset = m.get("charset", "utf8mb4")
        return (
            f"mariadb+asyncmy://{m['username']}:{m['password']}"
            f"@{m['host']}:{m.get('port', 3306)}/{m['database']}"
            f"?charset={charset}"
        )
    # Default: SQLite
    path = db.get("sqlite", {}).get(
        "path", os.path.join(os.path.dirname(__file__), "library.db")
    )
    return f"sqlite+aiosqlite:///{path}"


# Resolve once at import time
_settings = load_settings()
DATABASE_URL: str = build_database_url(_settings)
