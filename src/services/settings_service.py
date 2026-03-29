"""Service for loading, saving, and building database settings."""

from config import load_settings, save_settings, build_database_url, SETTINGS_PATH


class SettingsService:
    """Handles persistence and URL generation for application settings."""

    @property
    def settings_path(self) -> str:
        """Return the path to the settings YAML file."""
        return SETTINGS_PATH

    def load(self) -> dict:
        """Load settings from disk.

        Returns:
            The parsed settings dictionary.
        """
        return load_settings()

    def save(self, settings: dict) -> None:
        """Persist settings to disk.

        Args:
            settings: The settings dictionary to write.
        """
        save_settings(settings)

    def build_url(self, settings: dict) -> str:
        """Build a database URL from settings.

        Args:
            settings: The full settings dictionary.

        Returns:
            An async SQLAlchemy database URL string.
        """
        return build_database_url(settings)
