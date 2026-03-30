"""Async users view for managing application users (admin only)."""

import asyncio
import flet as ft
from views.base_view import BaseView
from components.entity_card import EntityCard, StatusBadge
from components.dialogs import FormDialog, ConfirmDialog
from services.container import ServiceContainer
from models.entities import AppUser


class UsersView(BaseView):
    """View for CRUD operations on application users."""

    def __init__(self, page: ft.Page, container: ServiceContainer):
        super().__init__(page, container)
        self._list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=5)

    async def build(self) -> ft.Control:
        await self.refresh()
        return ft.Column([
            ft.Row([
                ft.Text("User Management", size=28, weight=ft.FontWeight.BOLD),
                ft.Button("Add User", icon=ft.Icons.PERSON_ADD,
                          on_click=lambda e: asyncio.ensure_future(self._open_form())),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self._list,
        ], spacing=15, expand=True)

    async def refresh(self, e=None) -> None:
        users = await self._services.users.get_all()
        self._list.controls = [self._build_card(u) for u in users]
        self._page.update()

    def _build_card(self, user: AppUser) -> EntityCard:
        role_color = ft.Colors.ORANGE if user.is_admin else ft.Colors.BLUE_GREY
        content = ft.Row([
            ft.Container(width=50, height=50, bgcolor=ft.Colors.GREY_300, border_radius=25,
                         content=ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS if user.is_admin else ft.Icons.PERSON,
                                         size=26, color=ft.Colors.GREY_600)),
            ft.Column([
                ft.Text(user.display_name or user.username, weight=ft.FontWeight.BOLD, size=16),
                ft.Row([
                    ft.Text(f"@{user.username}", size=12, color=ft.Colors.GREY_500),
                    ft.Text(user.email or "", size=12, color=ft.Colors.GREY_500),
                    StatusBadge(user.role, role_color),
                ], spacing=10),
            ], expand=True, spacing=3),
        ], spacing=10)

        return EntityCard(
            content=content,
            on_edit=lambda e, u=user: asyncio.ensure_future(self._open_form(u)),
            on_delete=lambda e, u=user: asyncio.ensure_future(self._confirm_delete(u)),
        )

    async def _open_form(self, user: AppUser | None = None):
        username_f = ft.TextField(label="Username", value=user.username if user else "")
        display_f = ft.TextField(label="Display Name", value=user.display_name if user else "")
        email_f = ft.TextField(label="Email", value=user.email if user else "")
        password_f = ft.TextField(label="Password" + (" (leave blank to keep)" if user else ""),
                                  password=True, can_reveal_password=True)
        role_f = ft.Dropdown(
            label="Role", value=user.role if user else "user",
            options=[ft.dropdown.Option("admin"), ft.dropdown.Option("user")],
        )

        async def save():
            if not username_f.value.strip():
                username_f.error_text = "Required"
                self._page.update()
                return False
            if not user and not password_f.value:
                password_f.error_text = "Required"
                self._page.update()
                return False
            if user:
                await self._services.users.update(
                    user.id, username_f.value.strip(), display_f.value.strip(),
                    role_f.value, password_f.value, email_f.value.strip())
            else:
                await self._services.users.create(
                    username_f.value.strip(), password_f.value,
                    display_f.value.strip(), role_f.value, email_f.value.strip())
                # Send welcome email
                await self._services.mail.send_welcome_user(
                    display_f.value.strip(), username_f.value.strip(), email_f.value.strip())
            await self.refresh()
            return True

        FormDialog(self._page, "Edit User" if user else "Add User",
                   [username_f, display_f, email_f, password_f, role_f], save).show()

    async def _confirm_delete(self, user: AppUser):
        async def do_delete():
            await self._services.users.delete(user.id)
            await self.refresh()

        ConfirmDialog(self._page, "Delete User",
                      f'Delete user "{user.username}"?', do_delete).show()
