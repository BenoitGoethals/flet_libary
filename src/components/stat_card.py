"""Reusable statistic card component for dashboard displays."""

import flet as ft


class StatCard(ft.Container):
    """A card component that displays a statistic with an icon, title, and value.

    Args:
        title: Label text displayed above the value.
        value: The numeric or string value to display prominently.
        icon: Flet icon name to display alongside the title.
        color: Color applied to the icon and value text.
    """

    def __init__(self, title: str, value: int | str, icon: str, color: str):
        super().__init__(
            content=ft.Column(
                [
                    ft.Row(
                        [ft.Icon(icon, color=color, size=30), ft.Text(title, size=14, color=ft.Colors.GREY_600)],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Text(str(value), size=36, weight=ft.FontWeight.BOLD, color=color),
                ],
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            padding=20,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            expand=True,
        )
