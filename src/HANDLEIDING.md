# Handleiding — Bibliotheek Beheer Applicatie

## Inhoudsopgave

1. [Installatie & Opstarten](#installatie--opstarten)
2. [Navigatie](#navigatie)
3. [Dashboard](#dashboard)
4. [Boeken beheren](#boeken-beheren)
5. [Klanten beheren](#klanten-beheren)
6. [Opslaglocaties beheren](#opslaglocaties-beheren)
7. [Uitleningen beheren](#uitleningen-beheren)
8. [Instellingen](#instellingen)
9. [Testen uitvoeren](#testen-uitvoeren)
10. [Veelgestelde vragen](#veelgestelde-vragen)

---

## Installatie & Opstarten

### Vereisten

- Python 3.11 of hoger
- pip (Python package manager)

### Installatie

```bash
cd src
pip install flet sqlalchemy aiosqlite greenlet pyyaml
```

### Opstarten

```bash
cd src
flet run main.py
```

Bij de eerste keer opstarten worden automatisch aangemaakt:
- **`library.db`** — de SQLite-database met vooraf geladen voorbeelddata (20 boeken, 20 klanten, opslaglocaties en 10 uitleningen)
- **`settings.yml`** — het instellingenbestand met standaard SQLite-configuratie

---

## Navigatie

De applicatie heeft een **navigatiebalk** aan de linkerkant met zes schermen:

| Icoon | Scherm | Omschrijving |
|---|---|---|
| Dashboard | **Dashboard** | Overzicht met statistieken en actieve uitleningen |
| Boek | **Books** | Boeken zoeken, toevoegen, bewerken en verwijderen |
| Personen | **Clients** | Klanten zoeken, toevoegen, bewerken en verwijderen |
| Magazijn | **Storages** | Opslaglocaties beheren |
| Pijlen | **Rentals** | Boeken uitlenen, retourneren en historie bekijken |
| Tandwiel | **Settings** | Database-instellingen configureren |

Klik op een item in de navigatiebalk om naar het betreffende scherm te navigeren.

---

## Dashboard

Het dashboard toont een overzicht van de gehele bibliotheek in zes statistiekkaarten:

| Kaart | Betekenis |
|---|---|
| **Total Books** | Totaal aantal boeken in de bibliotheek |
| **Available** | Aantal boeken dat beschikbaar is voor uitlening |
| **Rented Out** | Aantal boeken dat momenteel is uitgeleend |
| **Clients** | Totaal aantal geregistreerde klanten |
| **Active Rentals** | Aantal lopende uitleningen |
| **Overdue** | Aantal uitleningen die over de retourdatum heen zijn |

Onder de statistieken staat een tabel met de **actieve uitleningen** (maximaal 10), met per regel:
- Boektitel
- Klantnaam
- Uitleendatum
- Retourdatum
- Status (Active / OVERDUE)

Klik op het **ververs-icoon** rechtsboven om de gegevens bij te werken.

---

## Boeken beheren

### Overzicht

Het Books-scherm toont alle boeken als kaarten. Elke kaart bevat:
- **Titel** en **auteur**
- **Status** badge (AVAILABLE / RENTED)
- **ISBN** en **genre** (indien ingevuld)
- **Locatie** — de opslaglocatie of de naam van de klant die het boek heeft geleend

### Zoeken

Typ een zoekterm in het zoekveld en druk op **Enter** of klik op het vergrootglas. Er wordt gezocht op:
- Titel
- Auteur
- ISBN

Maak het zoekveld leeg en zoek opnieuw om alle boeken te tonen.

### Boek toevoegen

1. Klik op **Add Book** rechtsboven.
2. Vul de velden in:
   - **Title** (verplicht)
   - **Author**
   - **ISBN**
   - **Genre**
   - **Storage** — kies een opslaglocatie uit de lijst (optioneel)
3. Klik op **Save**.

### Boek bewerken

1. Klik op het **potlood-icoon** op de kaart van het boek.
2. Pas de gewenste velden aan.
3. Klik op **Save**.

### Boek verwijderen

1. Klik op het **prullenbak-icoon** op de kaart van het boek.
2. Bevestig de verwijdering in het dialoogvenster met **Delete**.

---

## Klanten beheren

### Overzicht

Het Clients-scherm toont alle klanten als kaarten. Elke kaart bevat:
- **Naam**
- **E-mail** en **telefoon**
- **Adres** (indien ingevuld)
- Badge met het **aantal actieve uitleningen**

### Zoeken

Typ een zoekterm in het zoekveld. Er wordt gezocht op:
- Naam
- E-mailadres

### Klant toevoegen

1. Klik op **Add Client** rechtsboven.
2. Vul de velden in:
   - **Name** (verplicht)
   - **Email**
   - **Phone**
   - **Address**
3. Klik op **Save**.

### Klant bewerken

1. Klik op het **potlood-icoon** op de kaart.
2. Pas de gewenste velden aan.
3. Klik op **Save**.

### Klant verwijderen

1. Klik op het **prullenbak-icoon** op de kaart.
2. Bevestig met **Delete**.

---

## Opslaglocaties beheren

### Overzicht

Het Storages-scherm toont alle opslaglocaties als kaarten. Elke kaart bevat:
- **Naam** van de locatie
- **Locatiebeschrijving** (bijv. "Room 1")
- **Capaciteit** — voortgangsbalk met het aantal boeken ten opzichte van de maximale capaciteit
  - Groen: minder dan 75% vol
  - Oranje: 75%–95% vol
  - Rood: meer dan 95% vol

### Opslaglocatie toevoegen

1. Klik op **Add Storage** rechtsboven.
2. Vul de velden in:
   - **Name** (verplicht)
   - **Location** (beschrijving van de fysieke locatie)
   - **Capacity** (maximaal aantal boeken)
3. Klik op **Save**.

### Opslaglocatie bewerken

1. Klik op het **potlood-icoon** op de kaart.
2. Pas de gewenste velden aan.
3. Klik op **Save**.

### Opslaglocatie verwijderen

1. Klik op het **prullenbak-icoon** op de kaart.
2. Bevestig met **Delete**.

**Let op:** Bij het verwijderen van een opslaglocatie worden boeken die daar staan losgekoppeld (ze krijgen geen locatie meer).

---

## Uitleningen beheren

Het Rentals-scherm heeft twee tabbladen: **Active Rentals** en **History**.

### Boek uitlenen

1. Klik op **Rent Out Book** rechtsboven.
2. Selecteer in het dialoogvenster:
   - **Book** — kies een beschikbaar boek uit de lijst
   - **Client** — kies een klant
   - **Due date** — de retourdatum in formaat `JJJJ-MM-DD` (standaard 14 dagen vanaf vandaag)
3. Klik op **Save**.

Het boek krijgt de status "rented" en verschijnt in de lijst met actieve uitleningen.

**Opmerking:** Als er geen beschikbare boeken of geen klanten zijn, verschijnt er een melding.

### Boek retourneren

1. Ga naar het tabblad **Active Rentals**.
2. Klik op **Return** bij de betreffende uitlening.
3. Selecteer de **opslaglocatie** waar het boek wordt teruggeplaatst.
4. Klik op **Save**.

Het boek krijgt de status "available" en wordt gekoppeld aan de gekozen opslaglocatie. De uitlening verdwijnt uit de actieve lijst en verschijnt in de historie.

**Tip:** Een boek kan worden teruggebracht naar een andere locatie dan waar het vandaan kwam.

### Actieve uitleningen

Het tabblad **Active Rentals** toont per uitlening:
- Boektitel
- Klantnaam en telefoonnummer
- Uitleendatum en retourdatum
- **OVERDUE** badge als de retourdatum is verstreken

### Historie

Het tabblad **History** toont alle uitleningen (actief en geretourneerd) met:
- Boektitel
- Klantnaam
- Uitleendatum
- Retourdatum (of `-` als het boek nog niet is teruggebracht)
- Status badge (Active / Returned)

---

## Instellingen

Het Settings-scherm maakt het mogelijk om de database-verbinding te configureren zonder code aan te passen.

### Database-type kiezen

Klik op een van de knoppen om het database-type te selecteren:
- **SQLite** — lokaal bestand, geen server nodig (standaard)
- **MSSQL** — Microsoft SQL Server
- **MariaDB** — MariaDB / MySQL-compatibel

De configuratievelden worden automatisch aangepast aan het gekozen type.

### SQLite configureren

| Veld | Omschrijving |
|---|---|
| **Database file path** | Volledig pad naar het `.db`-bestand |

### MSSQL configureren

| Veld | Omschrijving |
|---|---|
| **Host** | Servernaam of IP-adres |
| **Port** | Poortnummer (standaard: 1433) |
| **Database** | Naam van de database |
| **Username** | Gebruikersnaam |
| **Password** | Wachtwoord (verborgen, klik op het oog-icoon om te tonen) |
| **ODBC Driver** | Naam van de ODBC-driver (standaard: `ODBC Driver 18 for SQL Server`) |

### MariaDB configureren

| Veld | Omschrijving |
|---|---|
| **Host** | Servernaam of IP-adres |
| **Port** | Poortnummer (standaard: 3306) |
| **Database** | Naam van de database |
| **Username** | Gebruikersnaam |
| **Password** | Wachtwoord (verborgen) |
| **Charset** | Tekenset (standaard: `utf8mb4`) |

### Opslaan

1. Configureer de gewenste velden.
2. Controleer de **Resulting database URL** onderaan — deze toont de URL die zal worden gebruikt.
3. Klik op **Save Settings**.
4. **Herstart de applicatie** om de wijzigingen door te voeren.

De instellingen worden opgeslagen in het bestand `settings.yml` in de `src/`-map. Dit bestand kan ook handmatig worden bewerkt.

### Extra drivers installeren

Afhankelijk van het gekozen database-type moet een extra Python-driver worden geinstalleerd:

```bash
# SQLite (standaard meegeleverd)
pip install aiosqlite

# MSSQL
pip install aioodbc

# MariaDB
pip install asyncmy
```

---

## Testen uitvoeren

De applicatie bevat 47 geautomatiseerde tests.

### Alle tests uitvoeren

```bash
cd src
python -m pytest tests/ -v
```

### Alleen integratietests uitvoeren

```bash
python -m pytest tests/test_book_integration.py tests/test_client_integration.py tests/test_storage_integration.py tests/test_rental_integration.py tests/test_dashboard_integration.py -v
```

### Alleen settings-tests uitvoeren

```bash
python -m pytest tests/test_settings.py -v
```

### Testoverzicht

| Testbestand | Aantal | Wat wordt getest |
|---|---|---|
| `test_book_integration.py` | 10 | Boeken: aanmaken, bewerken, verwijderen, zoeken, beschikbaarheid, sortering |
| `test_client_integration.py` | 7 | Klanten: aanmaken, bewerken, verwijderen, zoeken, actieve uitleningen, sortering |
| `test_storage_integration.py` | 5 | Opslaglocaties: aanmaken, bewerken, verwijderen, boektelling, sortering |
| `test_rental_integration.py` | 8 | Uitleningen: uitlenen, retourneren, andere locatie, historie, te laat, locatieweergave |
| `test_dashboard_integration.py` | 5 | Dashboard: lege statistieken, tellingen na data, uitleenstatistieken, retourstatistieken |
| `test_settings.py` | 12 | Configuratie: URL-opbouw per database-type, YAML laden/opslaan, SettingsService |

De integratietests gebruiken een **in-memory SQLite-database** en vereisen geen externe databaseserver.

---

## Veelgestelde vragen

### Waar staat de database?

Standaard wordt een SQLite-bestand `library.db` aangemaakt in de `src/`-map. Het pad is configureerbaar via de Settings-pagina.

### Kan ik de database wisselen zonder code te wijzigen?

Ja. Ga naar **Settings**, selecteer het gewenste database-type, vul de verbindingsgegevens in, klik op **Save Settings** en herstart de applicatie.

### Wat gebeurt er als ik een boek verwijder dat is uitgeleend?

Het boek en de bijbehorende uitlening worden verwijderd. Verwijder bij voorkeur eerst de uitlening door het boek te retourneren.

### Kan een klant meerdere boeken tegelijk lenen?

Ja. Een klant kan onbeperkt boeken tegelijk lenen. Het aantal actieve uitleningen wordt getoond op de klantkaart.

### Wat betekent "OVERDUE"?

Een uitlening is **overdue** (te laat) wanneer de huidige datum voorbij de opgegeven retourdatum is. Deze uitleningen worden rood gemarkeerd op het dashboard en in de actieve uitleningenlijst.

### Hoe kan ik een boek terugbrengen naar een andere locatie?

Bij het retourneren kies je de opslaglocatie waar het boek naartoe gaat. Dit hoeft niet dezelfde locatie te zijn als waar het boek vandaan kwam.

### Het settings.yml bestand is corrupt — wat nu?

Verwijder het bestand `settings.yml` uit de `src/`-map en herstart de applicatie. Er wordt automatisch een nieuw bestand aangemaakt met standaardinstellingen.

### Hoe voeg ik een nieuw database-type toe?

1. Maak een nieuwe subklasse van `DatabaseSection` in `components/database_sections.py`.
2. Voeg de URL-logica toe aan `build_database_url()` in `config.py`.
3. Voeg de klasse toe aan `SettingsView.SECTIONS` in `views/settings_view.py`.
4. Voeg standaardwaarden toe aan `_DEFAULT_SETTINGS` in `config.py`.
