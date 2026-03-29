# Bibliotheek Beheer Applicatie

Een **volledig asynchroon** bibliotheekbeheersysteem gebouwd met [Flet](https://flet.dev) (Python), [SQLAlchemy 2.0](https://www.sqlalchemy.org/) async ORM en [aiosqlite](https://github.com/omnilib/aiosqlite). De applicatie maakt het mogelijk om boeken, klanten, opslaglocaties en uitleningen te beheren.

---

## Projectstructuur

```
src/
├── main.py                        # Startpunt van de applicatie (async)
├── config.py                      # YAML-configuratie laden/opslaan, database-URL opbouwen
├── settings.yml                   # Instellingenbestand (wordt automatisch aangemaakt)
├── library.db                     # SQLite database (wordt automatisch aangemaakt)
│
├── models/                        # Laag 1: Datamodellen
│   ├── entities.py                # SQLAlchemy ORM-modellen (Book, Client, Storage, Rental, DashboardStats)
│   └── database.py                # Async database-verbinding (singleton, async engine & sessions)
│
├── repositories/                  # Laag 2: Data-toegang (async)
│   ├── base.py                    # Abstracte basisklasse BaseRepository<T> met async sessies
│   ├── book_repository.py         # Async CRUD voor boeken
│   ├── client_repository.py       # Async CRUD voor klanten
│   ├── storage_repository.py      # Async CRUD voor opslaglocaties
│   └── rental_repository.py       # Async CRUD voor uitleningen
│
├── services/                      # Laag 3: Bedrijfslogica (async)
│   ├── book_service.py            # Logica rondom boeken
│   ├── client_service.py          # Logica rondom klanten
│   ├── storage_service.py         # Logica rondom opslaglocaties
│   ├── rental_service.py          # Logica rondom uitlenen en retourneren
│   ├── dashboard_service.py       # Statistieken voor het dashboard
│   ├── settings_service.py        # Laden/opslaan van instellingen (YAML)
│   └── container.py               # Dependency Injection container (ServiceContainer)
│
├── components/                    # Herbruikbare UI-componenten
│   ├── stat_card.py               # StatCard: kaart met statistiek
│   ├── entity_card.py             # EntityCard + StatusBadge: kaart voor entiteiten
│   ├── dialogs.py                 # FormDialog + ConfirmDialog (async callbacks)
│   ├── type_selector.py           # TypeSelector: herbruikbare toggle-knoppen
│   └── database_sections.py       # DatabaseSection (ABC), SqliteSection, MssqlSection, MariadbSection
│
├── views/                         # Laag 4: Weergaven (async schermen)
│   ├── base_view.py               # Abstracte basisklasse BaseView
│   ├── dashboard.py               # DashboardView: overzicht met statistieken
│   ├── books_view.py              # BooksView: boekenbeheer
│   ├── clients_view.py            # ClientsView: klantenbeheer
│   ├── storages_view.py           # StoragesView: opslagbeheer
│   ├── rentals_view.py            # RentalsView: uitleningen beheer
│   └── settings_view.py           # SettingsView: database-instellingen
│
├── tests/                         # Tests (pytest + pytest-asyncio)
│   ├── conftest.py                # Fixtures: in-memory SQLite database & ServiceContainer
│   ├── test_book_integration.py   # 10 async integratietests voor boeken
│   ├── test_client_integration.py # 7 async integratietests voor klanten
│   ├── test_storage_integration.py# 5 async integratietests voor opslaglocaties
│   ├── test_rental_integration.py # 8 async integratietests voor uitleningen
│   ├── test_dashboard_integration.py # 5 async integratietests voor dashboard
│   └── test_settings.py           # 12 unit tests voor configuratie & settings
│
└── assets/                        # Statische bestanden (iconen, afbeeldingen)
```

---

## Architectuur: Lagen

De applicatie volgt een **gelaagde architectuur** met vier lagen. Elke laag mag alleen de laag direct eronder aanroepen.

```
┌─────────────────────────────────────┐
│            Views (Schermen)         │  ← Gebruikersinterface
├─────────────────────────────────────┤
│           Services (Logica)         │  ← Bedrijfsregels & orkestratie
├─────────────────────────────────────┤
│       Repositories (Data-toegang)   │  ← SQL-queries & CRUD
├─────────────────────────────────────┤
│     Models (Entiteiten & Database)  │  ← Datastructuren & verbinding
└─────────────────────────────────────┘
```

### Laag 1: Models

**Doel:** Definieert de datastructuren en de asynchrone databaseverbinding.

- **`entities.py`** — SQLAlchemy ORM-modellen (`Book`, `Client`, `Storage`, `Rental`) met relaties en berekende properties (`Book.is_available`, `Book.location_display`, `Rental.is_overdue`). `DashboardStats` is een gewone klasse voor geaggregeerde statistieken.
- **`database.py`** — `Database`-klasse (singleton) met **async engine** (`create_async_engine`) en **async session factory** (`async_sessionmaker`). Ondersteunt SQLite, MSSQL en MariaDB.
- **`config.py`** — Laadt/bewaart instellingen uit `settings.yml` (YAML). Bouwt de database-URL op basis van het geselecteerde type.

### Laag 2: Repositories

**Doel:** Verzorgt alle communicatie met de database (CRUD-operaties).

- **`BaseRepository[T]`** — abstracte generieke basisklasse met `async get_all()`, `async add()`, `async update()`, `async delete()`. Bevat helpers `_detach()` en `_detach_one()` om ORM-objecten los te koppelen van de sessie.
- Concrete repositories (`BookRepository`, `ClientRepository`, `StorageRepository`, `RentalRepository`) implementeren deze async methoden plus entiteit-specifieke methoden.
- Gebruiken **async sessions** met eager loading (`joinedload`, `subqueryload`). Objecten worden losgekoppeld (expunged) voordat ze worden teruggegeven.

### Laag 3: Services

**Doel:** Bevat de bedrijfslogica en orkestreert repositories.

- **`BookService`** — combineert boekdata met uitleeninformatie.
- **`ClientService`** — verrijkt klantdata met actieve uitleningen.
- **`RentalService`** — coördineert uitlenen en retourneren.
- **`DashboardService`** — berekent alle statistieken.
- **`SettingsService`** — laadt/bewaart YAML-instellingen, bouwt database-URL.
- **`ServiceContainer`** — dependency injection container die alle repositories en services aanmaakt en koppelt.

### Laag 4: Views

**Doel:** De gebruikersinterface (Flet UI-componenten).

- **`BaseView`** — abstracte basisklasse met `async build()` en `async refresh()`.
- Concrete views: `DashboardView`, `BooksView`, `ClientsView`, `StoragesView`, `RentalsView`, `SettingsView`.
- Views gebruiken alleen services — nooit direct repositories of database.
- Alle event handlers zijn **async** en gebruiken `await`.
- Herbruikbare componenten: `StatCard`, `EntityCard`, `StatusBadge`, `FormDialog`, `ConfirmDialog`, `TypeSelector`, `DatabaseSection`.

---

## SOLID Principes

| Principe | Toepassing |
|---|---|
| **S**ingle Responsibility | Elke klasse heeft één verantwoordelijkheid. `BookRepository` doet alleen database-operaties, `BookService` alleen bedrijfslogica. `SettingsService` beheert alleen YAML-configuratie. Elke `DatabaseSection` beheert alleen de velden voor één database-type. |
| **O**pen/Closed | Nieuw database-type toevoegen = nieuwe `DatabaseSection`-subklasse + toevoegen aan `SettingsView.SECTIONS`. Nieuwe entiteit = nieuwe repository/service/view. Bestaande code blijft ongewijzigd. |
| **L**iskov Substitution | Alle repositories zijn inwisselbaar via `BaseRepository[T]`. Alle views via `BaseView`. Alle database-secties via `DatabaseSection`. |
| **I**nterface Segregation | `DatabaseSection` biedt alleen `key`, `label`, `build()`, `to_dict()`. Services bieden alleen methoden aan die views nodig hebben. |
| **D**ependency Inversion | Views hangen af van services, niet van repositories. Services hangen af van repositories, niet van de database. `SettingsView` hangt af van `SettingsService`, niet van `config.py` functies. Alles wordt gekoppeld in `ServiceContainer`. |

---

## Instellingen & Database wisselen

De database-configuratie wordt opgeslagen in **`settings.yml`** en kan worden aangepast via de **Settings**-pagina in de applicatie.

### Ondersteunde databases

| Database | Async driver | Standaard poort |
|---|---|---|
| **SQLite** | `aiosqlite` | — (bestandspad) |
| **MSSQL** | `aioodbc` | 1433 |
| **MariaDB** | `asyncmy` | 3306 |

### settings.yml structuur

```yaml
database:
  type: sqlite                          # sqlite, mssql, of mariadb
  sqlite:
    path: /pad/naar/library.db
  mssql:
    host: localhost
    port: 1433
    database: library
    username: ''
    password: ''
    driver: ODBC Driver 18 for SQL Server
  mariadb:
    host: localhost
    port: 3306
    database: library
    username: ''
    password: ''
    charset: utf8mb4
```

Wijzig het `type`-veld via de Settings-pagina of rechtstreeks in het bestand. Herstart de applicatie na een wijziging.

---

## Async Architectuur

De gehele applicatie is **volledig asynchroon**:

```
ft.run(main)  →  async main(page)  →  await container.init()  →  await app.start()
     │
     ▼
Views:        async build(), async refresh(), async event handlers
     │
     ▼
Services:     async create(), async search(), async rent_book(), ...
     │
     ▼
Repositories: async get_all(), async add(), async update(), async delete()
     │
     ▼
Database:     create_async_engine, async_sessionmaker, AsyncSession
```

- **Sessies:** `async with self._db.create_session() as session:` — alle queries zijn non-blocking
- **Eager loading:** `joinedload` en `subqueryload` voorkomen lazy loading na sessie-afsluiting
- **Expunge-patroon:** objecten worden losgekoppeld van de sessie zodat ze veilig buiten de `async with`-block gebruikt kunnen worden

---

## Verloop van de applicatie (Flow)

### Opstarten

1. `main.py` definieert `async main(page)`, aangeroepen door `ft.run(main)`.
2. `ServiceContainer` wordt aangemaakt en `await container.init()` initialiseert database en schema.
3. `LibraryApp` bouwt het navigatiemenu en laadt de `DashboardView`.

### Navigatie

1. Gebruiker klikt op een menu-item (bijv. "Books").
2. `async LibraryApp._navigate()` instantieert de bijbehorende view.
3. `await view.build()` bouwt de UI en roept `await view.refresh()` aan.

### Een boek uitlenen

1. Gebruiker klikt op "Rent Out Book" in het **Rentals**-scherm.
2. `FormDialog` toont beschikbare boeken, klanten en retourdatum.
3. `RentalService.rent_book()` maakt een `Rental` aan en wijzigt de boekstatus naar "rented".
4. De view herlaadt zichzelf.

### Een boek retourneren

1. Gebruiker klikt op "Return" bij een actieve uitlening.
2. `FormDialog` vraagt naar de opslaglocatie.
3. `RentalService.return_book()` markeert de uitlening als geretourneerd en wijzigt de boekstatus naar "available".
4. De view herlaadt zichzelf.

---

## Testen

**47 tests** draaien volledig asynchroon met `pytest-asyncio` op een in-memory SQLite database.

```bash
cd src
python -m pytest tests/ -v
```

| Testbestand | Aantal | Omschrijving |
|---|---|---|
| `test_book_integration.py` | 10 | CRUD, zoeken, beschikbaarheid, sortering |
| `test_client_integration.py` | 7 | CRUD, zoeken, actieve uitleningen, sortering |
| `test_storage_integration.py` | 5 | CRUD, boektelling, sortering |
| `test_rental_integration.py` | 8 | Uitlenen, retourneren, historie, te laat, locatie |
| `test_dashboard_integration.py` | 5 | Lege dashboard, tellingen, uitleenstatistieken |
| `test_settings.py` | 12 | URL-opbouw (SQLite/MSSQL/MariaDB), YAML laden/opslaan, SettingsService |

---

## Opstarten

```bash
cd src
pip install flet sqlalchemy aiosqlite greenlet pyyaml
flet run main.py
```

De SQLite-database (`library.db`) en het instellingenbestand (`settings.yml`) worden automatisch aangemaakt bij de eerste keer opstarten.
