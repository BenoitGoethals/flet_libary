# Bibliotheek Beheer Applicatie

Een bibliotheekbeheersysteem gebouwd met [Flet](https://flet.dev) (Python) en [SQLAlchemy](https://www.sqlalchemy.org/) ORM. De applicatie maakt het mogelijk om boeken, klanten, opslaglocaties en uitleningen te beheren.

---

## Projectstructuur

```
src/
├── main.py                    # Startpunt van de applicatie
├── library.db                 # SQLite database (wordt automatisch aangemaakt)
│
├── models/                    # Laag 1: Datamodellen
│   ├── entities.py            # Dataclasses (Book, Client, Storage, Rental, DashboardStats)
│   └── database.py            # Database-verbinding (singleton)
│
├── repositories/              # Laag 2: Data-toegang
│   ├── base.py                # Abstracte basisklasse BaseRepository<T>
│   ├── book_repository.py     # CRUD-operaties voor boeken
│   ├── client_repository.py   # CRUD-operaties voor klanten
│   ├── storage_repository.py  # CRUD-operaties voor opslaglocaties
│   └── rental_repository.py   # CRUD-operaties voor uitleningen
│
├── services/                  # Laag 3: Bedrijfslogica
│   ├── book_service.py        # Logica rondom boeken (zoeken, locatie ophalen)
│   ├── client_service.py      # Logica rondom klanten (zoeken, actieve uitleningen tellen)
│   ├── storage_service.py     # Logica rondom opslaglocaties
│   ├── rental_service.py      # Logica rondom uitlenen en retourneren
│   ├── dashboard_service.py   # Statistieken voor het dashboard
│   └── container.py           # Dependency Injection container (ServiceContainer)
│
├── components/                # Herbruikbare UI-componenten
│   ├── stat_card.py           # StatCard: kaart met statistiek
│   ├── entity_card.py         # EntityCard + StatusBadge: kaart voor entiteiten
│   └── dialogs.py             # FormDialog + ConfirmDialog: formulier- en bevestigingsdialogen
│
├── views/                     # Laag 4: Weergaven (schermen)
│   ├── base_view.py           # Abstracte basisklasse BaseView
│   ├── dashboard.py           # DashboardView: overzicht met statistieken
│   ├── books_view.py          # BooksView: boekenbeheer
│   ├── clients_view.py        # ClientsView: klantenbeheer
│   ├── storages_view.py       # StoragesView: opslagbeheer
│   └── rentals_view.py        # RentalsView: uitleningen beheer
│
└── assets/                    # Statische bestanden (iconen, afbeeldingen)
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

**Doel:** Definieert de datastructuren en de databaseverbinding.

- **`entities.py`** bevat SQLAlchemy ORM-modellen (`Book`, `Client`, `Storage`, `Rental`) met relaties en berekende properties zoals `Book.is_available`, `Book.location_display` en `Rental.is_overdue`. `DashboardStats` is een gewone klasse voor geaggregeerde statistieken.
- **`database.py`** bevat de `Database`-klasse als singleton. Deze beheert de SQLAlchemy engine, session factory en maakt het schema aan bij de eerste keer opstarten.

### Laag 2: Repositories

**Doel:** Verzorgt alle communicatie met de database (CRUD-operaties).

- **`BaseRepository[T]`** is een abstracte generieke basisklasse die de interface afdwingt: `get_all()`, `add()`, `update()`, `delete()`. Bevat ook helpers `_detach()` en `_detach_one()` om ORM-objecten los te koppelen van de sessie.
- Elke concrete repository (`BookRepository`, `ClientRepository`, `StorageRepository`, `RentalRepository`) implementeert deze methoden plus eventuele extra methoden specifiek voor die entiteit.
- Repositories ontvangen een `Database`-instantie via hun constructor (dependency injection).
- Repositories gebruiken SQLAlchemy sessions met eager loading (`joinedload`, `subqueryload`) om relaties in één query op te halen. Objecten worden losgekoppeld van de sessie (expunged) voordat ze worden teruggegeven.

### Laag 3: Services

**Doel:** Bevat de bedrijfslogica en orkestreert repositories.

- Elke service klasse ontvangt de benodigde repositories via de constructor.
- **`BookService`** combineert boekdata met uitleeninformatie om de locatie van een boek te bepalen.
- **`ClientService`** verrijkt klantdata met het aantal actieve uitleningen.
- **`RentalService`** coördineert het uitlenen (status boek wijzigen + uitlening aanmaken) en retourneren (status boek wijzigen + opslaglocatie toewijzen).
- **`DashboardService`** berekent alle statistieken voor het dashboard.
- **`ServiceContainer`** is de dependency injection container: hij maakt alle repositories en services aan en koppelt ze aan elkaar. De hele applicatie gebruikt één `ServiceContainer`-instantie.

### Laag 4: Views

**Doel:** De gebruikersinterface (Flet UI-componenten).

- **`BaseView`** is een abstracte basisklasse met `build()` (bouwt de UI op) en `refresh()` (herlaadt de data).
- Elke view (`DashboardView`, `BooksView`, `ClientsView`, `StoragesView`, `RentalsView`) erft hiervan.
- Views gebruiken alleen services — ze raken nooit direct de repositories of database aan.
- Herbruikbare UI-elementen staan in `components/`: `StatCard`, `EntityCard`, `StatusBadge`, `FormDialog`, `ConfirmDialog`.

---

## SOLID Principes

| Principe | Toepassing |
|---|---|
| **S**ingle Responsibility | Elke klasse heeft één verantwoordelijkheid. `BookRepository` doet alleen database-operaties voor boeken, `BookService` doet alleen bedrijfslogica voor boeken. |
| **O**pen/Closed | Nieuwe entiteiten toevoegen vereist alleen nieuwe repository/service/view klassen. Bestaande code hoeft niet aangepast te worden. `BaseRepository` en `BaseView` zijn open voor uitbreiding. |
| **L**iskov Substitution | Alle concrete repositories zijn inwisselbaar met `BaseRepository[T]`. Alle views zijn inwisselbaar met `BaseView`. |
| **I**nterface Segregation | Services bieden alleen methoden aan die views nodig hebben. Repositories bieden alleen methoden aan die services nodig hebben. |
| **D**ependency Inversion | Views zijn afhankelijk van services (abstractie), niet van repositories. Services zijn afhankelijk van repositories, niet van de database. Alles wordt gekoppeld in `ServiceContainer`. |

---

## Verloop van de applicatie (Flow)

### Opstarten

1. `main.py` maakt een `LibraryApp`-instantie aan.
2. `LibraryApp` maakt een `ServiceContainer` aan → deze initialiseert de database, repositories en services.
3. Het navigatiemenu (`NavigationRail`) wordt opgebouwd.
4. De `DashboardView` wordt als eerste geladen.

### Navigatie

1. Gebruiker klikt op een menu-item (bijv. "Books").
2. `LibraryApp._on_nav_change()` wordt aangeroepen.
3. De bijbehorende view-klasse wordt geïnstantieerd met `page` en `ServiceContainer`.
4. `view.build()` bouwt de UI op en roept `view.refresh()` aan om data te laden.
5. Het content-gebied wordt bijgewerkt.

### Een boek uitlenen (voorbeeld)

1. Gebruiker opent het **Rentals**-scherm en klikt op "Rent Out Book".
2. `RentalsView._open_rent()` haalt beschikbare boeken en klanten op via de services.
3. Een `FormDialog` wordt getoond met dropdowns voor boek, klant en retourdatum.
4. Bij opslaan roept de view `RentalService.rent_book()` aan.
5. De service maakt een nieuwe `Rental` aan via `RentalRepository.add()`.
6. De service wijzigt de boekstatus naar "rented" via `BookRepository.update_status()`.
7. De view herlaadt zichzelf met `refresh()`.

### Een boek retourneren (voorbeeld)

1. Gebruiker klikt op "Return" bij een actieve uitlening.
2. Een `FormDialog` vraagt naar de opslaglocatie.
3. Bij opslaan roept de view `RentalService.return_book()` aan.
4. De service markeert de uitlening als geretourneerd via `RentalRepository.mark_returned()`.
5. De service wijzigt de boekstatus naar "available" en koppelt de opslaglocatie via `BookRepository.update_status()`.
6. De view herlaadt zichzelf.

---

## Opstarten

```bash
cd src
flet run main.py
```

De SQLite-database (`library.db`) wordt automatisch aangemaakt bij de eerste keer opstarten.
