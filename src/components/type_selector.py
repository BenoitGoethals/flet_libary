"""Reusable toggle-button selector component."""

import flet as ft
from typing import Callable, Awaitable


class TypeSelector(ft.Row):
    """A row of toggle buttons where exactly one is active at a time.

    Args:
        options: List of (key, label) tuples.
        value: The initially selected key.
        on_change: Async callback invoked with the new key on selection.
    """

    _ACTIVE = ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
    _INACTIVE = ft.ButtonStyle(bgcolor=ft.Colors.GREY_300, color=ft.Colors.BLACK)

    def __init__(self, options: list[tuple[str, str]], value: str,
                 on_change: Callable[[str], Awaitable[None]]):
        self._value = value
        self._on_change = on_change
        self._buttons: dict[str, ft.ElevatedButton] = {}
        controls = [ft.Text("Database type:", weight=ft.FontWeight.BOLD)]
        for key, label in options:
            async def _on_click(e, k=key):
                await self._select(k)
            btn = ft.ElevatedButton(label, on_click=_on_click)
            self._buttons[key] = btn
            controls.append(btn)
        super().__init__(controls=controls, spacing=10)
        self._style_buttons()

    @property
    def value(self) -> str:
        """The currently selected key."""
        return self._value

    def _style_buttons(self):
        """Apply active/inactive styles based on current value."""
        for key, btn in self._buttons.items():
            btn.style = self._ACTIVE if key == self._value else self._INACTIVE

    async def _select(self, key: str):
        """Handle a button click, update styles and fire callback."""
        self._value = key
        self._style_buttons()
        await self._on_change(key)
