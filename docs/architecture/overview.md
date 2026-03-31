# Architecture Overview

The Library Manager follows a **layered architecture** with dependency injection, keeping each layer focused on a single responsibility.

## Layers

```
┌─────────────────────────────────────────────┐
│                   Views                      │
│  (Flet UI — pages the user interacts with)   │
├─────────────────────────────────────────────┤
│                Components                    │
│  (Reusable UI widgets: cards, dialogs, …)    │
├─────────────────────────────────────────────┤
│                 Services                     │
│  (Business logic, validation, orchestration) │
├─────────────────────────────────────────────┤
│               Repositories                   │
│  (Async CRUD via SQLAlchemy sessions)        │
├─────────────────────────────────────────────┤
│                 Models                       │
│  (ORM entities + database engine)            │
└─────────────────────────────────────────────┘
```

## Dependency Injection

`ServiceContainer` wires all dependencies at startup:

- Creates repository instances
- Injects repositories into services
- Exposes services to views

Views receive the container and access only the services they need.

## Data Flow

1. **User action** triggers a view method (e.g., clicking "Add Book").
2. The **view** calls the appropriate **service** method.
3. The **service** applies business rules, then delegates to a **repository**.
4. The **repository** opens an async SQLAlchemy session, executes the query, and returns detached ORM objects.
5. The **view** updates the UI with the result.

## Database Support

The app supports multiple backends through SQLAlchemy's async engine:

| Backend  | Driver      | Config key  |
|----------|-------------|-------------|
| SQLite   | aiosqlite   | `sqlite`    |
| MSSQL    | aioodbc     | `mssql`     |
| MariaDB  | asyncmy     | `mariadb`   |

The active backend is selected in `settings.yml` and can be changed at runtime through the Settings view.

## Email Notifications

`MailService` sends SMTP emails for:

- Welcome messages for new users
- Rental confirmations
- Return confirmations
- Due-date reminders (2 days before)
- Overdue notices

A background loop in `main.py` checks active rentals every hour and triggers reminders automatically.
