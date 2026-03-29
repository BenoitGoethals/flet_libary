"""Dashboard view displaying library statistics and active rentals."""

import flet as ft
from views.base_view import BaseView
from components.stat_card import StatCard
from services.container import ServiceContainer


class DashboardView(BaseView):
    """Displays aggregate library statistics and a table of active rentals."""

    def __init__(self, page: ft.Page, container: ServiceContainer):
        """Initialize the dashboard view.

        Args:
            page: The Flet page instance.
            container: The service container for accessing business logic.
        """
        super().__init__(page, container)
        self._cards_row1 = ft.Row(spacing=15)
        self._cards_row2 = ft.Row(spacing=15)
        self._rentals_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Book")),
                ft.DataColumn(ft.Text("Client")),
                ft.DataColumn(ft.Text("Rented")),
                ft.DataColumn(ft.Text("Due")),
                ft.DataColumn(ft.Text("Status")),
            ],
            rows=[],
        )

    async def build(self) -> ft.Control:
        """Build the dashboard layout with stat cards and active rentals table.

        Returns:
            A scrollable Column containing the dashboard UI.
        """
        await self.refresh()
        return ft.Column(
            [
                ft.Row(
                    [ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD),
                     ft.IconButton(ft.Icons.REFRESH, on_click=lambda e: self.refresh())],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                self._cards_row1,
                self._cards_row2,
                ft.Divider(),
                ft.Text("Active Rentals", size=20, weight=ft.FontWeight.W_600),
                ft.Container(
                    content=self._rentals_table,
                    border_radius=8,
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                    padding=10,
                ),
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    async def refresh(self, e=None) -> None:
        """Refresh dashboard statistics and the active rentals table."""
        stats = await self._services.dashboard.get_stats()
        self._cards_row1.controls = [
            StatCard("Total Books", stats.total_books, ft.Icons.MENU_BOOK, ft.Colors.BLUE),
            StatCard("Available", stats.available, ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN),
            StatCard("Rented Out", stats.rented, ft.Icons.OUTPUT, ft.Colors.ORANGE),
        ]
        self._cards_row2.controls = [
            StatCard("Clients", stats.total_clients, ft.Icons.PEOPLE, ft.Colors.PURPLE),
            StatCard("Active Rentals", stats.active_rentals, ft.Icons.SWAP_HORIZ, ft.Colors.TEAL),
            StatCard("Overdue", stats.overdue, ft.Icons.WARNING, ft.Colors.RED),
        ]

        rentals = await self._services.rentals.get_active()
        self._rentals_table.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(r.book.title)),
                ft.DataCell(ft.Text(r.client.name)),
                ft.DataCell(ft.Text(r.rented_date_short)),
                ft.DataCell(ft.Text(r.due_date or "")),
                ft.DataCell(
                    ft.Text("OVERDUE", color=ft.Colors.RED, weight=ft.FontWeight.BOLD)
                    if r.is_overdue else ft.Text("Active", color=ft.Colors.GREEN)
                ),
            ])
            for r in rentals[:10]
        ]
        self._page.update()
