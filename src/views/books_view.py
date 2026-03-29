"""Async books view for managing the book catalog."""

import asyncio
import flet as ft
from views.base_view import BaseView
from components.entity_card import EntityCard, StatusBadge
from components.dialogs import FormDialog, ConfirmDialog
from services.container import ServiceContainer
from models.entities import Book


class BooksView(BaseView):
    """View for searching, adding, editing, and deleting books."""

    def __init__(self, page: ft.Page, container: ServiceContainer):
        super().__init__(page, container)
        self._search = ft.TextField(label="Search books...", expand=True,
                                    on_submit=lambda e: asyncio.ensure_future(self.refresh()))
        self._list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=5)
        self._file_picker = ft.FilePicker()

    async def build(self) -> ft.Control:
        """Build the books view layout.

        Returns:
            A Column containing the search bar, add button, and book list.
        """
        self._page.services.append(self._file_picker)
        await self.refresh()
        return ft.Column([
            ft.Row([
                ft.Text("Books", size=28, weight=ft.FontWeight.BOLD),
                ft.Row([self._search, ft.IconButton(ft.Icons.SEARCH, on_click=lambda e: asyncio.ensure_future(self.refresh()))], expand=True),
                ft.Button("Add Book", icon=ft.Icons.ADD, on_click=lambda e: asyncio.ensure_future(self._open_form())),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self._list,
        ], spacing=15, expand=True)

    async def refresh(self, e=None) -> None:
        """Refresh the book list from the database."""
        books = await self._services.books.search(self._search.value or "")
        self._list.controls = [self._build_card(b) for b in books]
        self._page.update()

    def _build_card(self, book: Book) -> EntityCard:
        """Build a card widget for a single book."""
        status_color = ft.Colors.GREEN if book.is_available else ft.Colors.ORANGE

        # Create photo display
        photo = None
        if book.photo_path:
            photo = ft.Image(src=book.photo_path, width=60, height=80, fit=ft.BoxFit.COVER, border_radius=4)

        content = ft.Row([
            photo if photo else ft.Container(width=60, height=80, bgcolor=ft.Colors.GREY_300, border_radius=4,
                                            content=ft.Icon(ft.Icons.BOOK, size=30, color=ft.Colors.GREY_600)),
            ft.Column([
                ft.Text(book.title, weight=ft.FontWeight.BOLD, size=16),
                ft.Text(f"by {book.author}" if book.author else "Unknown author", size=13, color=ft.Colors.GREY_500),
                ft.Row([
                    StatusBadge(book.status.upper(), status_color),
                    ft.Text(f"ISBN: {book.isbn}" if book.isbn else "", size=11, color=ft.Colors.GREY_500),
                    ft.Text(f"Genre: {book.genre}" if book.genre else "", size=11, color=ft.Colors.GREY_500),
                    ft.Text(book.location_display, size=12, color=ft.Colors.GREY_600),
                ], spacing=10),
            ], expand=True, spacing=3),
        ], spacing=10)

        return EntityCard(
            content=content,
            on_edit=lambda e, b=book: asyncio.ensure_future(self._open_form(b)),
            on_delete=lambda e, b=book: asyncio.ensure_future(self._confirm_delete(b)),
        )

    async def _open_form(self, book: Book | None = None):
        """Open the add/edit book dialog."""
        storages = await self._services.storages.get_all()
        options = [ft.dropdown.Option(key="", text="None")] + [
            ft.dropdown.Option(key=str(s.id), text=s.name) for s in storages
        ]
        title_f = ft.TextField(label="Title", value=book.title if book else "")
        author_f = ft.TextField(label="Author", value=book.author if book else "")
        isbn_f = ft.TextField(label="ISBN", value=book.isbn if book else "")
        genre_f = ft.TextField(label="Genre", value=book.genre if book else "")
        storage_f = ft.Dropdown(label="Storage", options=options,
                                value=str(book.storage_id) if book and book.storage_id else "")

        # Photo picker
        photo_path = book.photo_path if book else ""
        photo_display = ft.Text(photo_path or "No photo selected", size=12, color=ft.Colors.GREY_600)

        async def pick_photo(_):
            nonlocal photo_path
            files = await self._file_picker.pick_files(
                allow_multiple=False,
                allowed_extensions=["jpg", "jpeg", "png", "gif"]
            )
            if files:
                photo_path = files[0].path
                photo_display.value = photo_path
                self._page.update()

        photo_row = ft.Row([
            ft.Button("Choose Photo", icon=ft.Icons.IMAGE,
                     on_click=lambda e: asyncio.ensure_future(pick_photo(e))),
            photo_display,
        ], spacing=10)

        async def save():
            if not title_f.value.strip():
                title_f.error_text = "Required"
                self._page.update()
                return False
            sid = int(storage_f.value) if storage_f.value else None
            if book:
                await self._services.books.update(book.id, title_f.value, author_f.value, isbn_f.value, genre_f.value, sid, photo_path)
            else:
                await self._services.books.create(title_f.value, author_f.value, isbn_f.value, genre_f.value, sid, photo_path)
            await self.refresh()
            return True

        FormDialog(self._page, "Edit Book" if book else "Add Book",
                   [title_f, author_f, isbn_f, genre_f, storage_f, photo_row], save).show()

    async def _confirm_delete(self, book: Book):
        """Open the delete confirmation dialog."""
        async def do_delete():
            await self._services.books.delete(book.id)
            await self.refresh()

        ConfirmDialog(self._page, "Delete Book", f'Delete "{book.title}"?', do_delete).show()
