"""Async clients view for managing library clients."""

import flet as ft
from views.base_view import BaseView
from components.entity_card import EntityCard, StatusBadge
from components.dialogs import FormDialog, ConfirmDialog
from services.container import ServiceContainer
from models.entities import Client


class ClientsView(BaseView):
    """View for searching, adding, editing, and deleting clients."""

    def __init__(self, page: ft.Page, container: ServiceContainer):
        super().__init__(page, container)
        self._search = ft.TextField(label="Search clients...", expand=True,
                                    on_submit=lambda e: self.refresh())
        self._list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=5)

    async def build(self) -> ft.Control:
        """Build the clients view layout.

        Returns:
            A Column containing the search bar, add button, and client list.
        """
        await self.refresh()
        return ft.Column([
            ft.Row([
                ft.Text("Clients", size=28, weight=ft.FontWeight.BOLD),
                ft.Row([self._search, ft.IconButton(ft.Icons.SEARCH, on_click=lambda e: self.refresh())], expand=True),
                ft.ElevatedButton("Add Client", icon=ft.Icons.PERSON_ADD, on_click=lambda e: self._open_form()),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self._list,
        ], spacing=15, expand=True)

    async def refresh(self, e=None) -> None:
        """Refresh the client list from the database."""
        clients = await self._services.clients.search(self._search.value or "")
        self._list.controls = [self._build_card(c) for c in clients]
        self._page.update()

    def _build_card(self, client: Client) -> EntityCard:
        """Build a card widget for a single client."""
        n = client.active_rental_count
        content = ft.Column([
            ft.Text(client.name, weight=ft.FontWeight.BOLD, size=16),
            ft.Row([
                ft.Text(client.email or "", size=12, color=ft.Colors.GREY_500),
                ft.Text(client.phone or "", size=12, color=ft.Colors.GREY_500),
            ], spacing=15),
            ft.Row([
                ft.Text(client.address or "", size=12, color=ft.Colors.GREY_500) if client.address else ft.Container(),
                StatusBadge(f"{n} active rental{'s' if n != 1 else ''}", ft.Colors.TEAL if n else ft.Colors.GREY_400),
            ], spacing=10),
        ], expand=True, spacing=3)

        return EntityCard(
            content=content,
            on_edit=lambda e, c=client: self._open_form(c),
            on_delete=lambda e, c=client: self._confirm_delete(c),
        )

    async def _open_form(self, client: Client | None = None):
        """Open the add/edit client dialog."""
        name_f = ft.TextField(label="Name", value=client.name if client else "")
        email_f = ft.TextField(label="Email", value=client.email if client else "")
        phone_f = ft.TextField(label="Phone", value=client.phone if client else "")
        address_f = ft.TextField(label="Address", value=client.address if client else "")

        async def save():
            if not name_f.value.strip():
                name_f.error_text = "Required"
                self._page.update()
                return False
            if client:
                await self._services.clients.update(client.id, name_f.value, email_f.value, phone_f.value, address_f.value)
            else:
                await self._services.clients.create(name_f.value, email_f.value, phone_f.value, address_f.value)
            await self.refresh()
            return True

        FormDialog(self._page, "Edit Client" if client else "Add Client",
                   [name_f, email_f, phone_f, address_f], save).show()

    async def _confirm_delete(self, client: Client):
        """Open the delete confirmation dialog."""
        async def do_delete():
            await self._services.clients.delete(client.id)
            await self.refresh()

        ConfirmDialog(self._page, "Delete Client", f'Delete "{client.name}"?', do_delete).show()
