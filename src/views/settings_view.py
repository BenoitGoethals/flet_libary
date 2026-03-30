"""Settings view for configuring the database connection and mail server.

Composes TypeSelector, DatabaseSection components, and SettingsService
following the Single Responsibility and Open/Closed principles.
Adding a new database backend requires only a new DatabaseSection subclass.
"""

import flet as ft
from views.base_view import BaseView
from services.container import ServiceContainer
from components.type_selector import TypeSelector
from components.database_sections import DatabaseSection, SqliteSection, MssqlSection, MariadbSection


class SettingsView(BaseView):
    """View for editing database connection and mail server settings."""

    SECTIONS: list[type[DatabaseSection]] = [SqliteSection, MssqlSection, MariadbSection]

    def __init__(self, page: ft.Page, container: ServiceContainer):
        super().__init__(page, container)
        self._status = ft.Text("", size=13)
        self._sections: dict[str, DatabaseSection] = {}

    def _build_mail_section(self, mail_cfg: dict) -> ft.Control:
        """Build the mail server configuration fields."""
        self._mail_host = ft.TextField(label="SMTP Host", value=mail_cfg.get("host", ""), expand=True)
        self._mail_port = ft.TextField(label="Port", value=str(mail_cfg.get("port", 587)),
                                       width=100, keyboard_type=ft.KeyboardType.NUMBER)
        self._mail_username = ft.TextField(label="Username", value=mail_cfg.get("username", ""), expand=True)
        self._mail_password = ft.TextField(label="Password", value=mail_cfg.get("password", ""),
                                           password=True, can_reveal_password=True, expand=True)
        self._mail_from = ft.TextField(label="From Address", value=mail_cfg.get("from_address", ""), expand=True)
        self._mail_tls = ft.Checkbox(label="Use TLS", value=mail_cfg.get("use_tls", True))
        return ft.Column([
            ft.Text("Mail Server", weight=ft.FontWeight.BOLD, size=18),
            ft.Row([self._mail_host, self._mail_port], spacing=10),
            ft.Row([self._mail_username, self._mail_password], spacing=10),
            ft.Row([self._mail_from, self._mail_tls], spacing=10),
        ], spacing=10)

    def _mail_to_dict(self) -> dict:
        port = int(self._mail_port.value) if self._mail_port.value.isdigit() else 587
        return {
            "host": self._mail_host.value.strip(),
            "port": port,
            "username": self._mail_username.value.strip(),
            "password": self._mail_password.value,
            "from_address": self._mail_from.value.strip(),
            "use_tls": self._mail_tls.value,
        }

    async def build(self) -> ft.Control:
        """Build the settings form from composable components."""
        settings = self._services.settings.load()
        db = settings.get("database", {})
        mail_cfg = settings.get("mail", {})

        # Build each database section
        section_controls: list[ft.Control] = []
        for section_cls in self.SECTIONS:
            section = section_cls()
            cfg = db.get(section.key, {})
            control = section.build(cfg)
            self._sections[section.key] = section
            section_controls.append(control)

        # Type selector
        options = [(s.key, s.label) for s in self._sections.values()]
        self._type_selector = TypeSelector(
            options=options,
            value=db.get("type", "sqlite"),
            on_change=self._on_type_change,
        )

        self._section_controls = section_controls
        self._toggle_sections()

        # URL preview
        self._url_preview = ft.TextField(
            label="Resulting database URL", read_only=True,
            value=self._services.settings.build_url(settings), expand=True,
        )

        # Mail section
        mail_section = self._build_mail_section(mail_cfg)

        save_btn = ft.Button(
            "Save Settings", icon=ft.Icons.SAVE,
            on_click=self._save,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
        )

        self._init_status = ft.Text("", size=13)
        init_btn = ft.Button(
            "Initialize Database", icon=ft.Icons.STORAGE,
            on_click=self._init_database,
            style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE, color=ft.Colors.WHITE),
        )

        return ft.Column([
            ft.Text("Settings", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self._type_selector,
            *self._section_controls,
            ft.Divider(),
            self._url_preview,
            ft.Divider(),
            mail_section,
            ft.Divider(),
            ft.Row([save_btn, self._status], spacing=15, alignment=ft.MainAxisAlignment.START),
            ft.Divider(),
            ft.Text("Database Initialization", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("Create tables, indexes, and populate with sample data.",
                    size=13, color=ft.Colors.GREY_600),
            ft.Row([init_btn, self._init_status], spacing=15, alignment=ft.MainAxisAlignment.START),
            ft.Text(f"Settings file: {self._services.settings.settings_path}",
                    size=11, color=ft.Colors.GREY_500),
        ], spacing=15, expand=True, scroll=ft.ScrollMode.AUTO)

    async def refresh(self) -> None:
        """No dynamic data to refresh."""
        pass

    def _toggle_sections(self):
        """Show only the section matching the selected database type."""
        active_key = self._type_selector.value
        for section in self._sections.values():
            section._control.visible = section.key == active_key

    def _build_settings(self) -> dict:
        """Assemble a full settings dict from all section values."""
        return {
            "mail": self._mail_to_dict(),
            "database": {
                "type": self._type_selector.value,
                **{s.key: s.to_dict() for s in self._sections.values()},
            },
        }

    def _update_preview(self):
        """Update the URL preview field."""
        try:
            self._url_preview.value = self._services.settings.build_url(self._build_settings())
        except Exception:
            self._url_preview.value = "Invalid configuration"

    async def _on_type_change(self, db_type: str):
        """Handle database type toggle."""
        self._toggle_sections()
        self._update_preview()
        self._page.update()

    async def _init_database(self, e):
        """Create tables, indexes, and seed with sample data."""
        self._init_status.value = "Initializing..."
        self._init_status.color = ft.Colors.BLUE_700
        self._page.update()
        try:
            # Create tables and indexes
            await self._services.database.init_schema()

            # Seed sample data
            await self._services.storages.create("Main Library", "1st Floor, Building A", 500)
            await self._services.storages.create("Annex", "2nd Floor, Building B", 200)
            await self._services.storages.create("Archive", "Basement, Building A", 1000)

            # 20 clients
            await self._services.clients.create("Alice Martin", "alice.martin@example.com", "555-0101")
            await self._services.clients.create("Bob Dupont", "bob.dupont@example.com", "555-0102")
            await self._services.clients.create("Claire Bernard", "claire.bernard@example.com", "555-0103")
            await self._services.clients.create("David Leroy", "david.leroy@example.com", "555-0104")
            await self._services.clients.create("Emma Moreau", "emma.moreau@example.com", "555-0105")
            await self._services.clients.create("Francois Petit", "francois.petit@example.com", "555-0106")
            await self._services.clients.create("Gabrielle Roux", "gabrielle.roux@example.com", "555-0107")
            await self._services.clients.create("Hugo Lambert", "hugo.lambert@example.com", "555-0108")
            await self._services.clients.create("Isabelle Fournier", "isabelle.fournier@example.com", "555-0109")
            await self._services.clients.create("Julien Mercier", "julien.mercier@example.com", "555-0110")
            await self._services.clients.create("Karen Blanchard", "karen.blanchard@example.com", "555-0111")
            await self._services.clients.create("Louis Garnier", "louis.garnier@example.com", "555-0112")
            await self._services.clients.create("Marie Chevalier", "marie.chevalier@example.com", "555-0113")
            await self._services.clients.create("Nicolas Faure", "nicolas.faure@example.com", "555-0114")
            await self._services.clients.create("Olivia Girard", "olivia.girard@example.com", "555-0115")
            await self._services.clients.create("Pierre Bonnet", "pierre.bonnet@example.com", "555-0116")
            await self._services.clients.create("Quentin Andre", "quentin.andre@example.com", "555-0117")
            await self._services.clients.create("Rachel Lemaire", "rachel.lemaire@example.com", "555-0118")
            await self._services.clients.create("Sebastien Noel", "sebastien.noel@example.com", "555-0119")
            await self._services.clients.create("Therese Marchand", "therese.marchand@example.com", "555-0120")

            # 20 books (storage_id cycles 1-3)
            await self._services.books.create("The Great Gatsby", "F. Scott Fitzgerald", "978-0743273565", "Fiction", 1)
            await self._services.books.create("To Kill a Mockingbird", "Harper Lee", "978-0061120084", "Fiction", 2)
            await self._services.books.create("1984", "George Orwell", "978-0451524935", "Dystopian", 3)
            await self._services.books.create("Pride and Prejudice", "Jane Austen", "978-0141439518", "Romance", 1)
            await self._services.books.create("The Catcher in the Rye", "J.D. Salinger", "978-0316769488", "Fiction", 2)
            await self._services.books.create("Brave New World", "Aldous Huxley", "978-0060850524", "Dystopian", 3)
            await self._services.books.create("Les Miserables", "Victor Hugo", "978-0451419439", "Classic", 1)
            await self._services.books.create("The Little Prince", "Antoine de Saint-Exupery", "978-0156012195", "Fable", 2)
            await self._services.books.create("Moby Dick", "Herman Melville", "978-0142437247", "Adventure", 3)
            await self._services.books.create("War and Peace", "Leo Tolstoy", "978-0143039990", "Historical", 1)
            await self._services.books.create("Don Quixote", "Miguel de Cervantes", "978-0060934347", "Classic", 2)
            await self._services.books.create("Crime and Punishment", "Fyodor Dostoevsky", "978-0486415871", "Fiction", 3)
            await self._services.books.create("The Odyssey", "Homer", "978-0140268867", "Epic", 1)
            await self._services.books.create("Frankenstein", "Mary Shelley", "978-0141439471", "Gothic", 2)
            await self._services.books.create("Dracula", "Bram Stoker", "978-0141439846", "Gothic", 3)
            await self._services.books.create("Jane Eyre", "Charlotte Bronte", "978-0141441146", "Romance", 1)
            await self._services.books.create("Wuthering Heights", "Emily Bronte", "978-0141439556", "Romance", 2)
            await self._services.books.create("The Count of Monte Cristo", "Alexandre Dumas", "978-0140449266", "Adventure", 3)
            await self._services.books.create("Anna Karenina", "Leo Tolstoy", "978-0143035008", "Fiction", 1)
            await self._services.books.create("Madame Bovary", "Gustave Flaubert", "978-0140449129", "Fiction", 2)

            # Rent 10 books (book_id 1-10 to client_id 1-10)
            from datetime import date, timedelta
            today = date.today()
            for i in range(1, 11):
                due = (today + timedelta(days=14 - i)).isoformat()  # staggered due dates
                await self._services.rentals.rent_book(i, i, due)

            # Seed default users (admin/admin, user/user)
            await self._services.users.create("admin", "admin", "Administrator", "admin", "admin@library.local")
            await self._services.users.create("user", "user", "Regular User", "user", "user@library.local")

            self._init_status.value = "Database initialized with tables and sample data."
            self._init_status.color = ft.Colors.GREEN_700
        except Exception as ex:
            self._init_status.value = f"Error: {ex}"
            self._init_status.color = ft.Colors.RED_700
        self._page.update()

    async def _save(self, e):
        """Save settings to YAML and show confirmation."""
        settings = self._build_settings()
        self._services.settings.save(settings)
        self._update_preview()
        self._status.value = "Saved! Restart the app to apply changes."
        self._status.color = ft.Colors.GREEN_700
        self._page.update()
