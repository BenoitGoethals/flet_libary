"""Async rentals view for managing book rentals and returns."""

import asyncio
import flet as ft
from datetime import date, timedelta
from views.base_view import BaseView
from components.entity_card import StatusBadge
from components.dialogs import FormDialog
from services.container import ServiceContainer
from models.entities import Rental


class RentalsView(BaseView):
    """View for renting out books, returning them, and viewing history."""

    def __init__(self, page: ft.Page, container: ServiceContainer):
        super().__init__(page, container)
        self._active_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=5)
        self._history_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=5)
        self._tab_content = ft.Container(expand=True, padding=10)
        self._selected_tab = 0

    def _switch_tab(self, index: int):
        """Switch between Active Rentals and History tabs."""
        self._selected_tab = index
        self._tab_content.content = self._active_list if index == 0 else self._history_list
        self._active_btn.style = self._tab_style(index == 0)
        self._history_btn.style = self._tab_style(index == 1)
        self._page.update()

    @staticmethod
    def _tab_style(selected: bool) -> ft.ButtonStyle:
        """Get button style for tab buttons."""
        return ft.ButtonStyle(
            bgcolor=ft.Colors.PRIMARY if selected else ft.Colors.TRANSPARENT,
            color=ft.Colors.ON_PRIMARY if selected else ft.Colors.ON_SURFACE,
        )

    async def build(self) -> ft.Control:
        """Build the rentals view layout.

        Returns:
            A Column containing tab buttons, rental list, and action buttons.
        """
        self._active_btn = ft.Button("Active Rentals", on_click=lambda e: self._switch_tab(0),
                                              style=self._tab_style(True))
        self._history_btn = ft.Button("History", on_click=lambda e: self._switch_tab(1),
                                               style=self._tab_style(False))
        await self.refresh()
        self._tab_content.content = self._active_list
        return ft.Column([
            ft.Row([
                ft.Text("Rentals", size=28, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Button("Rent Out Book", icon=ft.Icons.OUTPUT,
                                      on_click=lambda e: asyncio.ensure_future(self._open_rent())),
                    ft.IconButton(ft.Icons.REFRESH, on_click=lambda e: asyncio.ensure_future(self.refresh())),
                ]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([self._active_btn, self._history_btn], spacing=5),
            self._tab_content,
        ], spacing=15, expand=True)

    async def refresh(self, e=None) -> None:
        """Refresh both active and history rental lists."""
        await self._refresh_active()
        await self._refresh_history()
        self._page.update()

    async def _refresh_active(self):
        """Refresh the active rentals list."""
        rentals = await self._services.rentals.get_active()
        self._active_list.controls = [self._build_active_card(r) for r in rentals]

    def _build_active_card(self, rental: Rental) -> ft.Container:
        """Build a card widget for an active rental."""
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(rental.book.title, weight=ft.FontWeight.BOLD, size=15),
                    ft.Text(f"Client: {rental.client.name} ({rental.client.phone or 'no phone'})",
                            size=12, color=ft.Colors.GREY_600),
                    ft.Row([
                        ft.Text(f"Rented: {rental.rented_date_short}", size=12),
                        ft.Text(f"Due: {rental.due_date or 'N/A'}", size=12,
                                color=ft.Colors.RED if rental.is_overdue else ft.Colors.GREY_600),
                    ], spacing=15),
                ], expand=True, spacing=3),
                ft.Column([
                    StatusBadge("OVERDUE", ft.Colors.RED) if rental.is_overdue else ft.Container(),
                    ft.Button("Return", icon=ft.Icons.KEYBOARD_RETURN,
                                      on_click=lambda e, r=rental: asyncio.ensure_future(self._open_return(r))),
                ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=5),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=15, border_radius=8,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            bgcolor=ft.Colors.SURFACE,
        )

    async def _refresh_history(self):
        """Refresh the rental history list."""
        rentals = await self._services.rentals.get_all()
        self._history_list.controls = [self._build_history_row(r) for r in rentals]

    def _build_history_row(self, rental: Rental) -> ft.Container:
        """Build a row widget for a rental history entry."""
        status = "Returned" if rental.returned_at else "Active"
        return ft.Container(
            content=ft.Row([
                ft.Text(rental.book.title, weight=ft.FontWeight.BOLD, expand=True),
                ft.Text(rental.client.name, width=120),
                ft.Text(rental.rented_date_short, width=90),
                ft.Text(rental.returned_date_short or "-", width=90),
                StatusBadge(status, ft.Colors.GREEN if rental.returned_at else ft.Colors.ORANGE),
            ]),
            padding=10, border_radius=6,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

    async def _open_rent(self):
        """Open the rent-out dialog."""
        available = await self._services.books.get_available()
        clients = await self._services.clients.get_all()
        if not available:
            self._page.open(ft.SnackBar(ft.Text("No available books to rent"), open=True))
            return
        if not clients:
            self._page.open(ft.SnackBar(ft.Text("No clients registered"), open=True))
            return

        book_dd = ft.Dropdown(
            label="Book", width=400,
            options=[ft.dropdown.Option(key=str(b.id), text=f"{b.title} - {b.author}") for b in available],
        )
        client_dd = ft.Dropdown(
            label="Client", width=400,
            options=[ft.dropdown.Option(key=str(c.id), text=c.name) for c in clients],
        )
        due_f = ft.TextField(label="Due date (YYYY-MM-DD)",
                             value=(date.today() + timedelta(days=14)).isoformat(), width=400)

        async def save():
            if not book_dd.value or not client_dd.value:
                return False
            await self._services.rentals.rent_book(int(book_dd.value), int(client_dd.value), due_f.value)
            await self.refresh()
            return True

        FormDialog(self._page, "Rent Out Book", [book_dd, client_dd, due_f], save).show()

    async def _open_return(self, rental: Rental):
        """Open the return-book dialog."""
        storages = await self._services.storages.get_all()
        storage_dd = ft.Dropdown(
            label="Return to storage", width=400,
            options=[ft.dropdown.Option(key=str(s.id), text=s.name) for s in storages],
        )

        async def save():
            if not storage_dd.value:
                return False
            await self._services.rentals.return_book(rental.id, int(storage_dd.value))
            await self.refresh()
            return True

        FormDialog(self._page, f"Return: {rental.book.title}", [
            ft.Text(f"Client: {rental.client.name}"), storage_dd
        ], save).show()
