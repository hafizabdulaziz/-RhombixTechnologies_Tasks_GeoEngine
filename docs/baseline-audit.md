# Baseline Audit Report - GeoTrace

## 1. Architectural Overview
GeoTrace (formerly GeoEngine Pro) is a Python-based geolocation platform using FastAPI for the web interface, SQLAlchemy for database persistence (SQLite), and a provider-based architecture with failover logic.

## 2. Component Inventory
- **API (FastAPI):** Exposes routes for dashboard, lookup, history, and health.
- **Services:**
  - `GeolocationService`: Core logic with failover using `FailoverService`.
  - `HistoryService`: Database interaction for logging lookups.
  - `MapService`: Leaflet-based map generation.
- **Providers:** Factory-based provider system (`IpApiProvider`).
- **Database:** SQLite with SQLAlchemy ORM (`LookupHistory` model).
- **Frontend:** TailwindCSS + Leaflet.js templates.

## 3. Database Schema
- `lookup_history`: Stores lookup details (id, ip, city, region, country, latitude, longitude, provider, timestamp).

## 4. Current Test State
- `tests/test_system.py`: 2 tests (System/Unit level).
- `tests/test_api.py`: 5 tests (API level).
- Status: All tests passing.

## 5. Known Limitations
- Hardcoded provider list (IpApiProvider only).
- Database file is local SQLite.
- Minimal error handling in some CLI commands.
- UI layout is vertically expansive.
