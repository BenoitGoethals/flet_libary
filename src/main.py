"""Main entry point for the Library Manager application."""

import asyncio
import logging
import flet as ft
from models.entities import AppUser
from services.container import ServiceContainer
from views.dashboard import DashboardView
from views.books_view import BooksView
from views.clients_view import ClientsView
from views.storages_view import StoragesView
from views.rentals_view import RentalsView
from views.settings_view import SettingsView
from views.users_view import UsersView
from views.login_view import LoginView
from views.base_view import BaseView


# All views with their nav label, icon, and whether admin-only
ALL_NAV = [
    ("Dashboard", ft.Icons.DASHBOARD, DashboardView, False),
    ("Books", ft.Icons.MENU_BOOK, BooksView, False),
    ("Clients", ft.Icons.PEOPLE, ClientsView, False),
    ("Storages", ft.Icons.WAREHOUSE, StoragesView, False),
    ("Rentals", ft.Icons.SWAP_HORIZ, RentalsView, False),
    ("Users", ft.Icons.MANAGE_ACCOUNTS, UsersView, True),
    ("Settings", ft.Icons.SETTINGS, SettingsView, True),
]


class LibraryApp:
    """Main application class managing navigation, auth, and view lifecycle."""

    def __init__(self, page: ft.Page, container: ServiceContainer):
        self._page = page
        self._container = container
        self._content_area = ft.Container(expand=True, padding=20)
        self._current_user: AppUser | None = None
        self._nav_entries: list[tuple] = []
        self._setup_page()

    def _setup_page(self):
        self._page.title = "Library Manager"
        self._page.padding = 0
        self._page.theme_mode = ft.ThemeMode.LIGHT
        self._page.window.width = 1100
        self._page.window.height = 750

    def _build_nav(self):
        """Build navigation entries filtered by user role."""
        is_admin = self._current_user and self._current_user.is_admin
        self._nav_entries = [
            (label, icon, view_cls)
            for label, icon, view_cls, admin_only in ALL_NAV
            if not admin_only or is_admin
        ]

    def _build_layout(self):
        self._build_nav()
        user_label = self._current_user.display_name or self._current_user.username
        role_label = self._current_user.role.upper()

        self._rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(icon=icon, label=label)
                for label, icon, _ in self._nav_entries
            ],
            on_change=self._on_nav_change,
            trailing=ft.Container(
                content=ft.Column([
                    ft.Divider(),
                    ft.Text(user_label, size=12, weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text(role_label, size=10, color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER),
                    ft.IconButton(ft.Icons.LOGOUT, tooltip="Logout",
                                  on_click=self._logout, icon_size=20),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                padding=ft.padding.only(bottom=10),
            ),
        )
        self._page.controls.clear()
        self._page.add(
            ft.Row([self._rail, ft.VerticalDivider(width=1), self._content_area], expand=True)
        )

    async def _on_nav_change(self, e):
        await self._navigate(e.control.selected_index)

    async def _navigate(self, index: int):
        view_cls = self._nav_entries[index][2]
        view = view_cls(self._page, self._container)
        self._content_area.content = await view.build()
        self._page.update()

    async def _on_login(self, user: AppUser):
        self._current_user = user
        self._build_layout()
        await self._navigate(0)

    async def _logout(self, e):
        self._current_user = None
        self._page.controls.clear()
        self._show_login()
        self._page.update()

    def _show_login(self):
        login = LoginView(self._page, self._container, self._on_login)
        self._page.add(login.build())

    async def start(self):
        self._show_login()
        self._page.update()


async def _reminder_loop(container: ServiceContainer):
    """Background task: check for due/overdue rentals and send emails every hour."""
    while True:
        try:
            active_rentals = await container.rentals.get_active()
            await container.mail.check_and_send_reminders(active_rentals)
        except Exception:
            logging.exception("Error in reminder loop")
        await asyncio.sleep(3600)  # every hour


async def main(page: ft.Page):
    """Async Flet application entry point."""
    container = ServiceContainer()
    await container.init()
    # Start background reminder task
    asyncio.ensure_future(_reminder_loop(container))
    app = LibraryApp(page, container)
    await app.start()


ft.run(main)
