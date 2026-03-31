# Library Manager

<div style="display:flex;align-items:center;gap:2rem;background:linear-gradient(135deg,#3f51b5 0%,#5c6bc0 100%);border-radius:16px;padding:2rem 2.5rem;margin-bottom:2rem;box-shadow:0 8px 32px rgba(63,81,181,0.25);">
  <img src="me.jpeg" alt="Author photo" style="width:110px;height:110px;border-radius:50%;object-fit:cover;border:4px solid rgba(255,255,255,0.85);box-shadow:0 4px 16px rgba(0,0,0,0.25);flex-shrink:0;" />
  <div style="color:#fff;">
    <div style="font-size:1.5rem;font-weight:700;letter-spacing:.5px;margin-bottom:.25rem;">Benoit Goethals</div>
    <div style="font-size:1rem;opacity:.85;margin-bottom:.75rem;">Developer · Flet Library Manager</div>
    <a href="https://github.com/BenoitGoethals/flet_libary" style="display:inline-block;background:rgba(255,255,255,0.18);color:#fff;text-decoration:none;padding:.35rem .9rem;border-radius:20px;font-size:.85rem;border:1px solid rgba(255,255,255,0.4);transition:background .2s;">GitHub Repository ↗</a>
  </div>
</div>

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
