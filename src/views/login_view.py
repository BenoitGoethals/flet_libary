"""Login view for user authentication."""

import flet as ft
from services.container import ServiceContainer


class LoginView:
    """Login form that authenticates users and returns the logged-in user."""

    def __init__(self, page: ft.Page, container: ServiceContainer, on_login):
        self._page = page
        self._services = container
        self._on_login = on_login
        self._username = ft.TextField(label="Username", autofocus=True, on_submit=self._do_login)
        self._password = ft.TextField(label="Password", password=True, can_reveal_password=True,
                                      on_submit=self._do_login)
        self._error = ft.Text("", color=ft.Colors.RED_700, size=13)

    def build(self) -> ft.Control:
        login_btn = ft.Button(
            "Login", icon=ft.Icons.LOGIN,
            on_click=self._do_login,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
        )
        return ft.Container(
            content=ft.Column([
                ft.Text("Library Manager", size=32, weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER),
                ft.Text("Please sign in", size=14, color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER),
                ft.Container(height=20),
                self._username,
                self._password,
                self._error,
                login_btn,
            ], width=350, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
        )

    async def _do_login(self, e):
        username = self._username.value.strip()
        password = self._password.value
        if not username or not password:
            self._error.value = "Please enter username and password."
            self._page.update()
            return
        user = await self._services.users.authenticate(username, password)
        if user:
            await self._on_login(user)
        else:
            self._error.value = "Invalid username or password."
            self._page.update()
