# Project Structure

```
src/
├── main.py                     # Application entry point
├── config.py                   # YAML settings loader
├── models/
│   ├── __init__.py
│   ├── database.py             # Async engine & session management
│   └── entities.py             # ORM models (Book, Client, Rental, …)
├── repositories/
│   ├── __init__.py
│   ├── base.py                 # Abstract CRUD interface
│   ├── book_repository.py
│   ├── client_repository.py
│   ├── rental_repository.py
│   ├── storage_repository.py
│   └── user_repository.py
├── services/
│   ├── __init__.py
│   ├── container.py            # Dependency injection container
│   ├── book_service.py
│   ├── client_service.py
│   ├── rental_service.py
│   ├── storage_service.py
│   ├── dashboard_service.py
│   ├── user_service.py
│   ├── mail_service.py
│   └── settings_service.py
├── views/
│   ├── __init__.py
│   ├── base_view.py            # Abstract view base class
│   ├── dashboard.py
│   ├── books_view.py
│   ├── clients_view.py
│   ├── rentals_view.py
│   ├── storages_view.py
│   ├── users_view.py
│   ├── settings_view.py
│   └── login_view.py
├── components/
│   ├── __init__.py
│   ├── entity_card.py          # Card & badge widgets
│   ├── stat_card.py            # Dashboard stat card
│   ├── dialogs.py              # Form & confirm dialogs
│   ├── type_selector.py        # Toggle-button selector
│   └── database_sections.py    # DB config form sections
└── tests/
    ├── conftest.py
    ├── test_book_integration.py
    ├── test_client_integration.py
    ├── test_dashboard_integration.py
    ├── test_rental_integration.py
    ├── test_settings.py
    └── test_storage_integration.py
```

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Flet app entry point, navigation, auth, background reminder loop |
| `config.py` | Loads/saves `settings.yml`, builds database URLs |
| `models/entities.py` | All SQLAlchemy ORM models and `DashboardStats` dataclass |
| `models/database.py` | Singleton async database manager |
| `services/container.py` | Wires repositories → services, initialises DB schema |
| `components/database_sections.py` | Extensible DB config sections (SQLite, MSSQL, MariaDB) |
