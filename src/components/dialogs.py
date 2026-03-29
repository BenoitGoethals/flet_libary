"""Reusable dialog components for forms and confirmation prompts."""

import flet as ft
from typing import Callable


class FormDialog:
    """Base class for entity form dialogs."""

    def __init__(self, page: ft.Page, title: str, fields: list[ft.Control], on_save: Callable):
        """Initialize the form dialog.

        Args:
            page: The Flet page to attach the dialog to.
            title: Dialog title text.
            fields: List of form field controls to display.
            on_save: Callback invoked on save. Should return True to close the dialog.
        """
        self._page = page
        self._on_save = on_save
        self._dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Column(fields, tight=True, spacing=10, width=400),
            actions=[
                ft.TextButton("Cancel", on_click=self._close),
                ft.ElevatedButton("Save", on_click=self._save),
            ],
        )

    def _save(self, e):
        """Handle the save button click event.

        Args:
            e: The click event.
        """
        if self._on_save():
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
    """A confirmation dialog with cancel and delete action buttons."""

    def __init__(self, page: ft.Page, title: str, message: str, on_confirm: Callable):
        """Initialize the confirmation dialog.

        Args:
            page: The Flet page to attach the dialog to.
            title: Dialog title text.
            message: Confirmation message to display.
            on_confirm: Callback invoked when the user confirms the action.
        """
        self._page = page
        self._dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close()),
                ft.ElevatedButton("Delete", on_click=lambda e: self._confirm(), color=ft.Colors.RED),
            ],
        )
        self._on_confirm = on_confirm

    def _confirm(self):
        """Execute the confirmation callback and close the dialog."""
        self._on_confirm()
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
