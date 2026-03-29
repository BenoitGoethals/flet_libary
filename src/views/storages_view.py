import flet as ft
from views.base_view import BaseView
from components.entity_card import EntityCard
from components.dialogs import FormDialog, ConfirmDialog
from services.container import ServiceContainer
from models.entities import Storage


class StoragesView(BaseView):
    def __init__(self, page: ft.Page, container: ServiceContainer):
        super().__init__(page, container)
        self._list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=5)

    def build(self) -> ft.Control:
        self.refresh()
        return ft.Column([
            ft.Row([
                ft.Text("Storages", size=28, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("Add Storage", icon=ft.Icons.ADD_BUSINESS, on_click=lambda e: self._open_form()),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self._list,
        ], spacing=15, expand=True)

    def refresh(self) -> None:
        storages = self._services.storages.get_all()
        self._list.controls = [self._build_card(s) for s in storages]
        self._page.update()

    def _build_card(self, storage: Storage) -> EntityCard:
        cap = storage.capacity or 0
        pct = (storage.book_count / cap) if cap > 0 else 0
        bar_color = ft.Colors.GREEN if pct < 0.75 else (ft.Colors.ORANGE if pct < 0.95 else ft.Colors.RED)

        content = ft.Column([
            ft.Text(storage.name, weight=ft.FontWeight.BOLD, size=16),
            ft.Text(storage.location or "No location", size=12, color=ft.Colors.GREY_500),
            ft.Row([
                ft.Text(f"{storage.book_count}/{cap} books", size=13),
                ft.ProgressBar(value=pct, width=150, color=bar_color, bgcolor=ft.Colors.GREY_300),
            ], spacing=10),
        ], expand=True, spacing=3)

        return EntityCard(
            content=content,
            on_edit=lambda e, s=storage: self._open_form(s),
            on_delete=lambda e, s=storage: self._confirm_delete(s),
        )

    def _open_form(self, storage: Storage | None = None):
        name_f = ft.TextField(label="Name", value=storage.name if storage else "")
        loc_f = ft.TextField(label="Location", value=storage.location if storage else "")
        cap_f = ft.TextField(label="Capacity", value=str(storage.capacity) if storage else "0",
                             keyboard_type=ft.KeyboardType.NUMBER)

        def save():
            if not name_f.value.strip():
                name_f.error_text = "Required"
                self._page.update()
                return False
            cap = int(cap_f.value) if cap_f.value.isdigit() else 0
            if storage:
                self._services.storages.update(storage.id, name_f.value, loc_f.value, cap)
            else:
                self._services.storages.create(name_f.value, loc_f.value, cap)
            self.refresh()
            return True

        FormDialog(self._page, "Edit Storage" if storage else "Add Storage",
                   [name_f, loc_f, cap_f], save).show()

    def _confirm_delete(self, storage: Storage):
        def do_delete():
            self._services.storages.delete(storage.id)
            self.refresh()

        ConfirmDialog(self._page, "Delete Storage",
                      f'Delete "{storage.name}"? Books will be unassigned.', do_delete).show()
