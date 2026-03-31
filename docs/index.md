# Library Manager

A cross-platform library management application built with [Flet](https://flet.dev) and [SQLAlchemy](https://www.sqlalchemy.org/).

## Features

- **Book Catalog Management** — Add, edit, search, and delete books with storage assignment
- **Client Management** — Track library members and their rental activity
- **Rental System** — Rent and return books with due-date tracking and overdue detection
- **Storage Locations** — Manage physical locations where books are stored
- **User Authentication** — Role-based access control (admin / user)
- **Email Notifications** — Automated reminders for due and overdue rentals
- **Multi-Database Support** — SQLite, MSSQL, and MariaDB backends
- **Dashboard** — Aggregated statistics and active rental overview

## Quick Start

```bash
# Install dependencies
uv sync

# Run as desktop app
uv run flet run src/main.py

# Run as web app
uv run flet run --web src/main.py
```

## Tech Stack

| Layer         | Technology                  |
|---------------|-----------------------------|
| UI Framework  | Flet (Flutter-based Python) |
| ORM           | SQLAlchemy (async)          |
| Database      | SQLite / MSSQL / MariaDB   |
| Config        | YAML (`settings.yml`)       |
| Email         | smtplib (SMTP)              |
| Testing       | pytest + pytest-asyncio     |

## Architecture

The application follows a **layered architecture** with clear separation of concerns:

```
Views → Services → Repositories → Database
  ↑         ↑
Components  Container (DI)
```

See the [Architecture Overview](architecture/overview.md) for details.
