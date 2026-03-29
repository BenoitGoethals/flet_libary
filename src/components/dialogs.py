"""Reusable async dialog components for forms and confirmation prompts."""

import asyncio
import flet as ft
from typing import Callable, Awaitable


class FormDialog:
    """Dialog for entity forms with async save callback."""

    def __init__(self, page: ft.Page, title: str, fields: list[ft.Control],
                 on_save: Callable[[], Awaitable[bool]]):
        """Initialize the form dialog.

        Args:
            page: The Flet page to attach the dialog to.
            title: Dialog title text.
            fields: List of form field controls to display.
            on_save: Async callback invoked on save. Should return True to close.
        """
        self._page = page
        self._on_save = on_save
        self._dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Column(fields, tight=True, spacing=10, width=400),
            actions=[
                ft.TextButton("Cancel", on_click=self._close),
                ft.Button("Save", on_click=self._save),
            ],
        )

    async def _save(self, e):
        """Handle the save button click event.

        Args:
            e: The click event.
        """
        if await self._on_save():
            self.close()

    def _close(self, e=None):
        """Handle the cancel button click event.

        Args:
            e: The click event, or None.
        """
        self.close()

    def close(self):
        """Close the dialog and update the page."""
        self._dialog.open = False
        self._page.update()

    def show(self):
        """Display the dialog by appending it to the page overlay."""
        self._page.overlay.append(self._dialog)
        self._dialog.open = True
        self._page.update()


class ConfirmDialog:
    """A confirmation dialog with async confirm callback."""

    def __init__(self, page: ft.Page, title: str, message: str,
                 on_confirm: Callable[[], Awaitable[None]]):
        """Initialize the confirmation dialog.

        Args:
            page: The Flet page to attach the dialog to.
            title: Dialog title text.
            message: Confirmation message to display.
            on_confirm: Async callback invoked when the user confirms.
        """
        self._page = page
        self._dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close()),
                ft.Button("Delete", on_click=lambda e: asyncio.ensure_future(self._confirm()),
                                  color=ft.Colors.RED),
            ],
        )
        self._on_confirm = on_confirm

    async def _confirm(self):
        """Execute the async confirmation callback and close the dialog."""
        await self._on_confirm()
        self.close()

    def close(self):
        """Close the dialog and update the page."""
        self._dialog.open = False
        self._page.update()

    def show(self):
        """Display the dialog by appending it to the page overlay."""
        self._page.overlay.append(self._dialog)
        self._dialog.open = True
        self._page.update()
