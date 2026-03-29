"""Main entry point for the Library Manager application."""

import flet as ft
from services.container import ServiceContainer
from views.dashboard import DashboardView
from views.books_view import BooksView
from views.clients_view import ClientsView
from views.storages_view import StoragesView
from views.rentals_view import RentalsView
from views.settings_view import SettingsView
from views.base_view import BaseView


class LibraryApp:
    """Main application class managing navigation and view lifecycle."""

    VIEW_CLASSES: list[type[BaseView]] = [
        DashboardView, BooksView, ClientsView, StoragesView, RentalsView, SettingsView,
    ]

    NAV_ITEMS = [
        ("Dashboard", ft.Icons.DASHBOARD),
        ("Books", ft.Icons.MENU_BOOK),
        ("Clients", ft.Icons.PEOPLE),
        ("Storages", ft.Icons.WAREHOUSE),
        ("Rentals", ft.Icons.SWAP_HORIZ),
        ("Settings", ft.Icons.SETTINGS),
    ]

    def __init__(self, page: ft.Page, container: ServiceContainer):
        """Initialize the application.

        Args:
            page: The Flet page instance.
            container: The initialized service container.
        """
        self._page = page
        self._container = container
        self._content_area = ft.Container(expand=True, padding=20)
        self._views: dict[int, BaseView] = {}
        self._setup_page()
        self._build_layout()

    def _setup_page(self):
        """Configure page properties."""
        self._page.title = "Library Manager"
        self._page.padding = 0
        self._page.theme_mode = ft.ThemeMode.LIGHT
        self._page.window.width = 1100
        self._page.window.height = 750

    def _build_layout(self):
        """Build the navigation rail and main layout."""
        self._rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(icon=icon, label=label)
                for label, icon in self.NAV_ITEMS
            ],
            on_change=self._on_nav_change,
        )
        self._page.add(
            ft.Row([self._rail, ft.VerticalDivider(width=1), self._content_area], expand=True)
        )

    async def _on_nav_change(self, e):
        """Handle navigation rail selection changes."""
        await self._navigate(e.control.selected_index)

    async def _navigate(self, index: int):
        """Navigate to a view by index.

        Args:
            index: The view index to navigate to.
        """
        view_cls = self.VIEW_CLASSES[index]
        view = view_cls(self._page, self._container)
        self._views[index] = view
        self._content_area.content = await view.build()
        self._page.update()

    async def start(self):
        """Load the initial view (dashboard)."""
        await self._navigate(0)


async def main(page: ft.Page):
    """Async Flet application entry point."""
    container = ServiceContainer()
    await container.init()
    app = LibraryApp(page, container)
    await app.start()


ft.run(main)
