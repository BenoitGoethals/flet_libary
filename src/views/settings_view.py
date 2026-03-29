"""Settings view for configuring the database connection.

Composes TypeSelector, DatabaseSection components, and SettingsService
following the Single Responsibility and Open/Closed principles.
Adding a new database backend requires only a new DatabaseSection subclass.
"""

import flet as ft
from views.base_view import BaseView
from services.container import ServiceContainer
from components.type_selector import TypeSelector
from components.database_sections import DatabaseSection, SqliteSection, MssqlSection, MariadbSection


class SettingsView(BaseView):
    """View for editing database connection settings stored in settings.yml."""

    SECTIONS: list[type[DatabaseSection]] = [SqliteSection, MssqlSection, MariadbSection]

    def __init__(self, page: ft.Page, container: ServiceContainer):
        super().__init__(page, container)
        self._status = ft.Text("", size=13)
        self._sections: dict[str, DatabaseSection] = {}

    async def build(self) -> ft.Control:
        """Build the settings form from composable components."""
        settings = self._services.settings.load()
        db = settings.get("database", {})

        # Build each database section
        section_controls: list[ft.Control] = []
        for section_cls in self.SECTIONS:
            section = section_cls()
            cfg = db.get(section.key, {})
            control = section.build(cfg)
            self._sections[section.key] = section
            section_controls.append(control)

        # Type selector
        options = [(s.key, s.label) for s in self._sections.values()]
        self._type_selector = TypeSelector(
            options=options,
            value=db.get("type", "sqlite"),
            on_change=self._on_type_change,
        )

        self._section_controls = section_controls
        self._toggle_sections()

        # URL preview
        self._url_preview = ft.TextField(
            label="Resulting database URL", read_only=True,
            value=self._services.settings.build_url(settings), expand=True,
        )

        save_btn = ft.Button(
            "Save Settings", icon=ft.Icons.SAVE,
            on_click=self._save,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
        )

        return ft.Column([
            ft.Text("Settings", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self._type_selector,
            *self._section_controls,
            ft.Divider(),
            self._url_preview,
            ft.Row([save_btn, self._status], spacing=15, alignment=ft.MainAxisAlignment.START),
            ft.Text(f"Settings file: {self._services.settings.settings_path}",
                    size=11, color=ft.Colors.GREY_500),
        ], spacing=15, expand=True, scroll=ft.ScrollMode.AUTO)

    async def refresh(self) -> None:
        """No dynamic data to refresh."""
        pass

    def _toggle_sections(self):
        """Show only the section matching the selected database type."""
        active_key = self._type_selector.value
        for section in self._sections.values():
            section._control.visible = section.key == active_key

    def _build_settings(self) -> dict:
        """Assemble a full settings dict from all section values."""
        return {
            "database": {
                "type": self._type_selector.value,
                **{s.key: s.to_dict() for s in self._sections.values()},
            },
        }

    def _update_preview(self):
        """Update the URL preview field."""
        try:
            self._url_preview.value = self._services.settings.build_url(self._build_settings())
        except Exception:
            self._url_preview.value = "Invalid configuration"

    async def _on_type_change(self, db_type: str):
        """Handle database type toggle."""
        self._toggle_sections()
        self._update_preview()
        self._page.update()

    async def _save(self, e):
        """Save settings to YAML and show confirmation."""
        settings = self._build_settings()
        self._services.settings.save(settings)
        self._update_preview()
        self._status.value = "Saved! Restart the app to apply changes."
        self._status.color = ft.Colors.GREEN_700
        self._page.update()
