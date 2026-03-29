"""Abstract base view defining the async interface for all application views."""

import flet as ft
from abc import ABC, abstractmethod
from services.container import ServiceContainer


class BaseView(ABC):
    """Abstract base class for all views in the library application.

    Provides access to the Flet page and the service container.
    """

    def __init__(self, page: ft.Page, container: ServiceContainer):
        """Initialize the base view.

        Args:
            page: The Flet page instance.
            container: The service container for accessing business logic.
        """
        self._page = page
        self._services = container

    @abstractmethod
    async def build(self) -> ft.Control:
        """Build and return the view's root Flet control.

        Returns:
            The root control representing this view's UI.
        """
        ...

    @abstractmethod
    async def refresh(self) -> None:
        """Refresh the view's data and update the display."""
        ...
