"""Unit tests for settings configuration: config module, SettingsService, and database sections."""

import os
import pytest
import yaml
from config import load_settings, save_settings, build_database_url
from services.settings_service import SettingsService


class TestBuildDatabaseUrl:
    """Tests for build_database_url with each database type."""

    def test_sqlite_url(self):
        """SQLite settings should produce an aiosqlite URL."""
        settings = {"database": {"type": "sqlite", "sqlite": {"path": "/tmp/test.db"}}}
        url = build_database_url(settings)
        assert url == "sqlite+aiosqlite:////tmp/test.db"

    def test_sqlite_default_when_unknown_type(self):
        """An unknown type should fall back to SQLite."""
        settings = {"database": {"type": "unknown", "sqlite": {"path": "/tmp/x.db"}}}
        url = build_database_url(settings)
        assert url.startswith("sqlite+aiosqlite:///")

    def test_mssql_url(self):
        """MSSQL settings should produce an aioodbc URL with encoded driver."""
        settings = {
            "database": {
                "type": "mssql",
                "mssql": {
                    "host": "dbserver",
                    "port": 1433,
                    "database": "libdb",
                    "username": "sa",
                    "password": "secret",
                    "driver": "ODBC Driver 18 for SQL Server",
                },
            },
        }
        url = build_database_url(settings)
        assert url == (
            "mssql+aioodbc://sa:secret@dbserver:1433/libdb"
            "?driver=ODBC+Driver+18+for+SQL+Server"
        )

    def test_mariadb_url(self):
        """MariaDB settings should produce an asyncmy URL with charset."""
        settings = {
            "database": {
                "type": "mariadb",
                "mariadb": {
                    "host": "mariahost",
                    "port": 3307,
                    "database": "books",
                    "username": "root",
                    "password": "pass",
                    "charset": "utf8mb4",
                },
            },
        }
        url = build_database_url(settings)
        assert url == "mariadb+asyncmy://root:pass@mariahost:3307/books?charset=utf8mb4"

    def test_mariadb_default_port(self):
        """MariaDB should default to port 3306 when not specified."""
        settings = {
            "database": {
                "type": "mariadb",
                "mariadb": {
                    "host": "localhost",
                    "database": "lib",
                    "username": "u",
                    "password": "p",
                },
            },
        }
        url = build_database_url(settings)
        assert ":3306/" in url

    def test_mssql_default_port(self):
        """MSSQL should default to port 1433 when not specified."""
        settings = {
            "database": {
                "type": "mssql",
                "mssql": {
                    "host": "h",
                    "database": "d",
                    "username": "u",
                    "password": "p",
                },
            },
        }
        url = build_database_url(settings)
        assert ":1433/" in url


class TestLoadSaveSettings:
    """Tests for loading and saving YAML settings files."""

    def test_save_and_load(self, tmp_path, monkeypatch):
        """Saved settings should be loadable and identical."""
        path = str(tmp_path / "settings.yml")
        monkeypatch.setattr("config.SETTINGS_PATH", path)
        data = {"database": {"type": "sqlite", "sqlite": {"path": "/tmp/test.db"}}}
        save_settings(data)
        loaded = load_settings()
        assert loaded == data

    def test_load_creates_default_if_missing(self, tmp_path, monkeypatch):
        """load_settings should create a default file if none exists."""
        path = str(tmp_path / "settings.yml")
        monkeypatch.setattr("config.SETTINGS_PATH", path)
        assert not os.path.exists(path)
        settings = load_settings()
        assert os.path.exists(path)
        assert settings["database"]["type"] == "sqlite"

    def test_saved_file_is_valid_yaml(self, tmp_path, monkeypatch):
        """The saved file should be parseable YAML."""
        path = str(tmp_path / "settings.yml")
        monkeypatch.setattr("config.SETTINGS_PATH", path)
        data = {"database": {"type": "mariadb", "mariadb": {"host": "h"}}}
        save_settings(data)
        with open(path, "r") as f:
            parsed = yaml.safe_load(f)
        assert parsed == data


class TestSettingsService:
    """Tests for the SettingsService wrapper."""

    def test_load_and_save_round_trip(self, tmp_path, monkeypatch):
        """Service save/load should round-trip correctly."""
        path = str(tmp_path / "settings.yml")
        monkeypatch.setattr("config.SETTINGS_PATH", path)
        svc = SettingsService()
        data = {"database": {"type": "sqlite", "sqlite": {"path": "/x.db"}}}
        svc.save(data)
        assert svc.load() == data

    def test_build_url_delegates(self):
        """Service build_url should return the same as config.build_database_url."""
        svc = SettingsService()
        settings = {"database": {"type": "sqlite", "sqlite": {"path": "/a.db"}}}
        assert svc.build_url(settings) == "sqlite+aiosqlite:////a.db"

    def test_settings_path_property(self):
        """settings_path should return a string ending with settings.yml."""
        svc = SettingsService()
        assert svc.settings_path.endswith("settings.yml")
