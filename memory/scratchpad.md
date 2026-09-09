# 📝 Operation APIx: Working Memory Scratchpad
### Active Operational Context, Live State & Cross-Session Memory
**Project**: Operation APIx (SIH26056 - Ministry of Statistics & Programme Implementation)  
**Last Synced**: September 9, 2026 | **Current Status**: PHASE 3 ACTIVE (Web Scrapers & Ingestion Adapters)

---

## 🎯 Current Target & Immediate Sprint
- **Active Phase**: **Phase 3 (Core Scraping Engine & Ingestion Adapters)**
- **Immediate Sprint 3A Focus**:
  1. `scrapers/base_scraper.py`: Abstract base scraper with TLS fingerprint impersonation (`curl_cffi` / Chrome 124 JA3), randomized human jitter (2.0s - 4.5s), automated user-agent rotation, and session lifecycle management.
  2. `scrapers/otas/easemytrip_scraper.py`: Anchor high-speed JSON XHR adapter targeting `https://flight.easemytrip.com/api/flight/search`.
  3. `scrapers/browser_engine.py`: Headless Playwright engine with `playwright-stealth` for Akamai Bot Manager (MakeMyTrip, IndiGo).
- **Recent Accomplishments (Phase 1 & Phase 2 Complete)**:
  - Verbatim Project Charter locked ([`SIH26056_PROJECT_CHARTER.md`](file:///c:/Users/swaya/Downloads/SIH/SIH26056_PROJECT_CHARTER.md)).
  - Comprehensive Edge Cases & Normalization Guide locked ([`EDGE_CASES_AND_DATA_NORMALIZATION_GUIDE.md`](file:///c:/Users/swaya/Downloads/SIH/EDGE_CASES_AND_DATA_NORMALIZATION_GUIDE.md)) with 15 documented edge cases and math proofs.
  - Complete project configuration in `config/` (`routes.json`, `sources.json`, `windows.json`, `settings.py`).
  - SQLite database initialized and seeded with 5,580 mock quotes across 30 days (`database/apix.db`).
  - Laspeyres Price Index engine tested and verified (`engine/laspeyres.py`), generating 31 daily APIx points.
  - Pydantic v2 data models (`pipeline/models.py`) and Data Sentinel quality guardian (`pipeline/sentinel.py`) passing 100% health checks.
  - Master CLI tool `manage.py` operational.

---

## 👥 Team Roster & Roles
- **Swayam (Lead)**: Fullstack development, web scraping, AI-assisted architecture, deployment, ML/DL integration.
- **Sukesh**: Fullstack web developer (React, Node.js, backend APIs, frontend component systems).
- **Shivam**: UI/UX specialist, design purifier, user experience flow, visual perfection.
- **Yash**: Team coordinator, sharp execution, logistics, timeline tracking, college SPOC liaison.
- **Open Slot 5**: Mandatory female teammate (SIH official rule - internal recruiting in progress).
- **Open Slot 6**: Domain researcher / co-speaker (civil aviation & tariff economics).

---

## 🧭 Active Matrix Parameters
- **Corridors (12 DGCA Routes)**:
  `DEL-BOM` (0.165), `DEL-BLR` (0.125), `BOM-BLR` (0.095), `DEL-CCU` (0.080), `BLR-HYD` (0.075), `MAA-DEL` (0.070), `DEL-HYD` (0.065), `BOM-GOI` (0.060), `DEL-PNQ` (0.055), `BOM-CCU` (0.055), `DEL-GAU` (0.050), `DEL-SXR` (0.050). Total weight = 1.000.
- **Booking Horizons (5 Windows)**:
  - $T+1$: Next-day departure (distressed yield pricing).
  - $T+7$: 1-week horizon (short-term corporate travel).
  - $T+15$: 2-week horizon (standard domestic leisure).
  - $T+30$: 1-month horizon (planned family/vacation).
  - $T+45$: Advance booking window (base promotional tariff).
- **Mandated Portals (11 Ingestion Targets)**:
  - **5 Direct Airlines**: IndiGo (`6E`), Air India (`AI`), Air India Express (`IX`), Akasa Air (`QP`), SpiceJet (`SG`).
  - **6 OTAs**: EaseMyTrip, MakeMyTrip, Ixigo, Yatra, Cleartrip, HappyEasyGo / Goibibo.
- **Base Year**: `2024 = 100` (strictly matching MoSPI revised CPI series).
- **Latest Computed Laspeyres APIx**: `108.91` (+4.19% 7-day surge).

---

## 📊 Infrastructure & Circuit Breaker Status
- **Local Database**: `database/apix.db` (SQLite 3, WAL mode enabled, 5,580 mock quotes + 31 index records).
- **Cloud Database Plan**: Supabase PostgreSQL (credentials configured in `.env`, connection toggle in `database/db.py`).
- **Notion Integration**: Workspace setup automated via `setup_notion_workspace.py` (Secret: Configured via `NOTION_TOKEN`).
- **Circuit Breakers**:
  - All 11 portals initialized in `HEALTHY` state in `state/circuit_breakers.json`.
  - Trip Threshold: 3 consecutive HTTP 403/429 or schema failures.
  - Cooldown: 1800s (30 minutes) before half-open probe.
- **Fail-safe Cache**: `database/cache/` (offline demo snapshot fallback).
