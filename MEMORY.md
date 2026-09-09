# 🧠 Operation APIx: Project Memory & Navigation Hub
### Smart India Hackathon (SIH 2026) | Problem Statement: SIH26056 (MoSPI)
**Repository**: `c:\Users\swaya\Downloads\SIH`  
**Last Synchronized**: September 9, 2026

---

## 🗂️ Memory System Structure

The long-term project memory for Operation APIx is organized into dedicated persistent Markdown documents inside the [`memory/`](file:///c:/Users/swaya/Downloads/SIH/memory) directory:

| Document | Purpose & Contents |
| :--- | :--- |
| [**`memory/scratchpad.md`**](file:///c:/Users/swaya/Downloads/SIH/memory/scratchpad.md) | **Active Operational Context & Live State**: Immediate target, active sprint tasks, circuit breaker states, and live DB stats. |
| [**`memory/PROJECT_MEMORY.md`**](file:///c:/Users/swaya/Downloads/SIH/memory/PROJECT_MEMORY.md) | **Master Knowledge Base & Source of Truth**: Full project charter, MoSPI mandate, team superpowers, statistical framework, edge cases, and portal intel. |
| [**`memory/CONVERSATION_HISTORY.md`**](file:///c:/Users/swaya/Downloads/SIH/memory/CONVERSATION_HISTORY.md) | **Complete Multi-Session Transcript Archive**: Comprehensive chronological log of all 10 project conversations (prompts, decisions, created artifacts). |
| [**`memory/DECISIONS_LOG.md`**](file:///c:/Users/swaya/Downloads/SIH/memory/DECISIONS_LOG.md) | **Architectural Decision Records (ADRs)**: 10 formal technical and economic decisions (Laspeyres formula, unbundling, SQLite to Supabase, 2-stage scraping). |

---

## 🚀 Quick Project Snapshot

- **Problem ID**: **SIH26056** (Ministry of Statistics and Programme Implementation - MoSPI / NSO).
- **Core Mission**: Build India's first real-time, high-frequency **Airfare Price Index (APIx)** using automated scraping across 11 portals, unbundling statutory fees, and calculating a DGCA passenger-weighted Laspeyres index (Base `2024 = 100`) for the **Reserve Bank of India (RBI)**.
- **Team**:
  - **Swayam** (Lead - Scraping, Fullstack, AI, ML)
  - **Sukesh** (Fullstack Dev - React, Node.js, Web APIs)
  - **Shivam** (UI/UX Specialist - Interface Flow & Polish)
  - **Yash** (Coordinator - Logistics, SPOC Liaison, Timing)
  - *Slot 5 (Open - Mandatory Female Teammate)*
  - *Slot 6 (Open - Domain Researcher / Pitcher)*
- **Parameters**: 12 DGCA Corridors (Total weight = 1.000) $\times$ 5 Booking Horizons ($T+1, T+7, T+15, T+30, T+45$) $\times$ 11 Portals (5 Airlines + 6 OTAs) = 660 queries/cycle.
- **Current Phase**: **Phase 3 Active (Web Scrapers & Ingestion Adapters)**.
  - Pre-requisites Complete: Project Charter locked, 15 Edge Cases locked, SQLite DB seeded (5,580 mock quotes + 31 index points), Sentinel watchdog verified, CLI `manage.py` operational.
  - Immediate Target: Build `scrapers/base_scraper.py` (TLS/JA3 impersonation + jitter) and `scrapers/otas/easemytrip_scraper.py`.

---

## 📚 Essential Project Documentation
- [`SIH26056_PROJECT_CHARTER.md`](file:///c:/Users/swaya/Downloads/SIH/SIH26056_PROJECT_CHARTER.md): Verbatim problem statement and government requirements.
- [`EDGE_CASES_AND_DATA_NORMALIZATION_GUIDE.md`](file:///c:/Users/swaya/Downloads/SIH/EDGE_CASES_AND_DATA_NORMALIZATION_GUIDE.md): 15 aviation edge cases, unbundling formulas, and Pydantic validators.
- [`TASK_BOARD.md`](file:///c:/Users/swaya/Downloads/SIH/TASK_BOARD.md): Live Kanban board and sprint deliverables.
- [`OPERATION_APIX_MASTER_TIMELINE.md`](file:///c:/Users/swaya/Downloads/SIH/OPERATION_APIX_MASTER_TIMELINE.md): Phase 1 to Phase 6 end-to-end schedule through December 2026.
- [`AIRFARE_PRICE_INDEX_MASTER_GUIDE.md`](file:///c:/Users/swaya/Downloads/SIH/AIRFARE_PRICE_INDEX_MASTER_GUIDE.md): Complete 15–20 minute pitch script & Obsidian chapter guide.
- [`presentation/index.html`](file:///c:/Users/swaya/Downloads/SIH/presentation/index.html): Interactive HTML5 pitch presentation deck.
