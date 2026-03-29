"""Reusable card and badge components for displaying entity information."""

import flet as ft
from typing import Callable


class EntityCard(ft.Container):
    """A card component that wraps entity content with optional edit and delete action buttons.

    Args:
        content: The Flet control to display as the card body.
        on_edit: Optional callback invoked when the edit button is clicked.
        on_delete: Optional callback invoked when the delete button is clicked.
    """

    def __init__(
        self,
        content: ft.Control,
        on_edit: Callable | None = None,
        on_delete: Callable | None = None,
    ):
        actions = ft.Row(spacing=0)
        if on_edit:
            actions.controls.append(ft.IconButton(ft.Icons.EDIT, on_click=on_edit, icon_size=18))
        if on_delete:
            actions.controls.append(ft.IconButton(ft.Icons.DELETE, on_click=on_delete, icon_size=18, icon_color=ft.Colors.RED))

        super().__init__(
            content=ft.Row(
                [content, actions],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            bgcolor=ft.Colors.SURFACE,
        )


class StatusBadge(ft.Container):
    """A small colored badge for displaying status text.

    Args:
        text: The status label to display.
        color: Background color of the badge.
    """

    def __init__(self, text: str, color: str):
        super().__init__(
            content=ft.Text(text, size=11, color=ft.Colors.WHITE),
            bgcolor=color,
            padding=ft.padding.symmetric(4, 8),
            border_radius=4,
        )
