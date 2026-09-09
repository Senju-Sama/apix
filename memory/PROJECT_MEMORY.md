# 🧠 Operation APIx: Master Project Memory & Knowledge Base
### Persistent Cross-Session Source of Truth for SIH 2026 (SIH26056)
**Project Title**: Real-Time Airfare Price Index for Indian Domestic Flights  
**Problem Statement ID**: SIH26056  
**Sponsoring Ministry**: Ministry of Statistics and Programme Implementation (MoSPI) / National Statistical Office (NSO)  
**Primary Beneficiary**: Reserve Bank of India (RBI) Monetary Policy Committee (CPI Transport Subgroup)  
**Target Milestone**: Grand Finale Victory (December 2026) | ₹1,00,000 National Prize

---

## 📌 1. Project Charter & National Economic Mandate

### The Core Problem (The Multi-Billion Rupee Blind Spot)
In India, **over 92% of domestic flight tickets are purchased online** through OTAs (EaseMyTrip, MakeMyTrip, Ixigo, Cleartrip, Yatra) and direct airline portals under high-frequency dynamic pricing algorithms that fluctuate every few minutes based on booking horizon, inventory velocity, and fuel costs.

Historically, statistical inflation metrics for domestic air transport in the Consumer Price Index (CPI) were recorded manually by field investigators visiting physical airline ticketing counters once per month to ask for standard published fares. 
- This manual process failed completely during dynamic surges (e.g., Diwali or holiday weekends where Delhi–Mumbai surges from ₹4,500 to ₹18,000).
- Under the newly revised **CPI Series (Base 2024 = 100)**, MoSPI mandated automated, high-frequency digital collection of domestic air tariffs.
- **Operation APIx** is the purpose-built statistical data collection, tariff unbundling, and real-time Laspeyres Index generation system engineered to solve this national data collection deficit.

### Key Institutional Stakeholders
1. **MoSPI / NSO**: Official sponsor; requires daily, weekly, and monthly statistical index time series.
2. **RBI**: Sets India's repo rate under Flexible Inflation Targeting (FIT: 4% ± 2%); relies on accurate CPI Transport data.
3. **DGCA & MoCA**: Provides route-level passenger traffic data for weighting factors ($W_i$) and regulatory oversight on air tariffs.

---

## 👥 2. Team Profile, Roster & Superpowers

| Name | Role | Core Competencies & Responsibilities |
| :--- | :--- | :--- |
| **Swayam** | **Team Leader & Architect** | Web scraping engineering, fullstack system architecture, AI-assisted rapid development, deployment, machine learning and deep learning integration. |
| **Sukesh** | **Fullstack Developer** | Frontend & Backend development, React, component architecture, state management, REST APIs, full web development. |
| **Shivam** | **UI/UX Specialist** | In-depth UX workflow, interface design purification, aesthetic polish, visualization layout, user empathy. |
| **Yash** | **Coordinator & Logistics** | Timely execution, team coordination, logistics, non-dev sharp problem analysis, College SPOC communications. |
| *Slot 5 (Open)* | *Mandatory Female Teammate* | Internal college recruitment in progress to satisfy SIH official eligibility requirement. |
| *Slot 6 (Open)* | *Domain Researcher / Pitcher* | Domain analysis of civil aviation tariffs, DGCA regulations, and co-pitching support. |

---

## 🏆 3. SIH 2026 Strategy & Winning Playbook

- **Zero-Competition Advantage**: SIH26056 was identified as having exceptionally low team saturation compared to generic consumer apps, giving the team high odds of national selection.
- **College Internal Screening**:
  - College SPOC quota: Maximum 45 teams per college (typically 30–35 software + 10–15 hardware).
  - Internal hackathon screening required before central portal nomination.
- **Judging Criteria Weightage**:
  1. *Problem Understanding & Clarity*: 20%
  2. *Innovation & Technical Feasibility*: 30%
  3. *Practicality, Scalability & Architecture*: 20%
  4. *User Experience & Visual Polish*: 15%
  5. *Economic & Government Impact*: 15%
- **Presentation Assets**:
  - Master pitch script & Obsidian blueprint: [`AIRFARE_PRICE_INDEX_MASTER_GUIDE.md`](file:///c:/Users/swaya/Downloads/SIH/AIRFARE_PRICE_INDEX_MASTER_GUIDE.md).
  - High-impact interactive presentation deck: [`presentation/index.html`](file:///c:/Users/swaya/Downloads/SIH/presentation/index.html).

---

## 📐 4. Mathematical & Statistical Framework

### The Laspeyres Price Index Formula
MoSPI and international national statistical standards require a base-weighted Laspeyres Price Index:
$$APIx_t = \frac{\sum_{i=1}^{n} (P_{i,t} \cdot Q_{i,0})}{\sum_{i=1}^{n} (P_{i,0} \cdot Q_{i,0})} \times 100 = \sum_{i=1}^{n} \left( W_i \cdot \frac{P_{i,t}}{P_{i,0}} \right) \times 100$$

Where:
- $P_{i,t}$: Cleaned average economic price on route $i$ at period $t$.
- $P_{i,0}$: Baseline average economic price on route $i$ (Base Year: `2024 = 100`).
- $W_i = \frac{P_{i,0} \cdot Q_{i,0}}{\sum (P_{i,0} \cdot Q_{i,0})}$: DGCA passenger traffic volume weight of route $i$ ($\sum W_i = 1.000$).

### 12 DGCA Domestic Route Corridors & Weights
1. `DEL-BOM` (Delhi ⇄ Mumbai): **0.165** (16.5% national weight)
2. `DEL-BLR` (Delhi ⇄ Bangalore): **0.125**
3. `BOM-BLR` (Mumbai ⇄ Bangalore): **0.095**
4. `DEL-CCU` (Delhi ⇄ Kolkata): **0.080**
5. `BLR-HYD` (Bangalore ⇄ Hyderabad): **0.075**
6. `MAA-DEL` (Chennai ⇄ Delhi): **0.070**
7. `DEL-HYD` (Delhi ⇄ Hyderabad): **0.065**
8. `BOM-GOI` (Mumbai ⇄ Goa Dabolim/Mopa): **0.060**
9. `DEL-PNQ` (Delhi ⇄ Pune): **0.055**
10. `BOM-CCU` (Mumbai ⇄ Kolkata): **0.055**
11. `DEL-GAU` (Delhi ⇄ Guwahati - Northeast connectivity): **0.050**
12. `DEL-SXR` (Delhi ⇄ Srinagar - Strategic high-volatility): **0.050**

### 5 Booking Horizons ($T+D$)
- **$T+1$**: Next-day departure (distressed yield, acute price spikes, business emergencies).
- **$T+7$**: 1-week horizon (short-term domestic corporate travel).
- **$T+15$**: 2-week horizon (standard consumer domestic travel).
- **$T+30$**: 1-month horizon (planned family/vacation travel).
- **$T+45$**: Advance booking window (promotional bucket baseline).

---

## 🛠️ 5. System Architecture & Autonomous Agent Assembly Line

### Directory Topology
```
SIH/
├── agents/registry.json          # 5 specialized agent personas & assembly line
├── config/                      # System-wide configuration
│   ├── routes.json              # 12 DGCA corridors & weights
│   ├── sources.json             # 11 mandated portals (5 airlines + 6 OTAs)
│   ├── windows.json             # 5 booking horizons (T+1 to T+45)
│   └── settings.py              # Environment settings & constants
├── database/                    # Persistence layer
│   ├── apix.db                  # Local SQLite WAL database (seeded)
│   ├── db.py                    # Connection manager (SQLite / Supabase toggle)
│   ├── schema.sql               # Dialect-agnostic SQL schema
│   ├── seed_mock_data.py        # 30-day realistic quote & index generator
│   └── cache/                   # Offline demo replay cache
├── engine/                      # Core statistical algorithms
│   └── laspeyres.py             # DGCA weighted Laspeyres index calculator
├── pipeline/                    # Quality assurance & normalization
│   ├── models.py                # Pydantic v2 schemas (Raw, Cleaned, Breakdown)
│   └── sentinel.py              # Schema watchdog & route coverage auditor
├── scrapers/                    # Ingestion adapters (Phase 3 active)
│   ├── base_scraper.py          # Abstract scraper with TLS & jitter (in dev)
│   ├── browser_engine.py        # Playwright stealth engine (in dev)
│   ├── airlines/                # Direct carrier adapters
│   └── otas/                    # OTA JSON/DOM adapters
├── state/                       # Pipeline persistence & fault tolerance
│   ├── checkpoint.json          # Resumable scraper checkpoint
│   ├── circuit_breakers.json    # Portal health states & trip logic
│   └── pipeline_state.json      # Live audit counts & quote stats
├── memory/                      # Persistent agent memory & logs
│   ├── scratchpad.md            # Active operational context
│   ├── PROJECT_MEMORY.md        # Master reference & source of truth
│   ├── CONVERSATION_HISTORY.md  # Complete multi-session dialogue archive
│   └── DECISIONS_LOG.md         # Architecture Decision Records (ADRs)
└── manage.py                    # Master CLI tool for all operations
```

### The 5 Specialized Agent Personas (`agents/registry.json`)
1. **`api-sniffer-agent`**: Reverse-engineers internal JSON endpoints (EaseMyTrip, Ixigo, Yatra, Cleartrip) via `curl_cffi` for sub-second responses with zero browser overhead.
2. **`stealth-scraper-agent`**: Operates headless Playwright with randomized viewports, human cursor jitter, and cookie handshakes to bypass Akamai Bot Manager (MakeMyTrip, IndiGo) and Cloudflare Turnstile.
3. **`tariff-auditor-agent`**: Strips statutory non-airline taxes, isolates OTA drip-pricing convenience charges, detects IQR price outliers, and imputes sold-out flight gaps.
4. **`data-sentinel-agent`**: Validates strict Pydantic v2 schemas, prevents corrupted quotes from touching the database, monitors circuit breakers, and verifies coverage.
5. **`backend-architect-agent`**: Serves asynchronous FastAPI REST endpoints for MoSPI/NSO/RBI and manages seamless migration from SQLite to Supabase.

---

## ✈️ 6. Aviation Tariffs, Unbundling & Edge Cases Summary

Synthesized from [`EDGE_CASES_AND_DATA_NORMALIZATION_GUIDE.md`](file:///c:/Users/swaya/Downloads/SIH/EDGE_CASES_AND_DATA_NORMALIZATION_GUIDE.md) (15 production edge cases):

1. **Pure Economic Fare Unbundling**:
   $$\text{Pure Economic Fare} = \text{Base Fare} + \text{Fuel Surcharge (YQ/YR)}$$
   *Excluded Statutory Add-ons*: User Development Fee (UDF/IN), Passenger Service Fee (PSF/ASF/YM), CUTE/User Charges, and K3 GST (5% Economy / 12% Business).
2. **The "Drip-Pricing" Convenience Fee Trap**:
   EaseMyTrip advertises ₹0 convenience fee; MakeMyTrip, Goibibo, and Yatra charge ₹399–₹499 per passenger per sector at checkout. Comparing checkout totals distorts airline pricing behavior by up to +12%. Convenience fees are stripped entirely.
3. **The "Lite" Hand-Baggage Trap**:
   7kg cabin-only "Lite" fares (e.g., IndiGo `R07LGT`) are ₹300–₹500 cheaper than standard 15kg check-in economy (`R07SAV`). Comparing a Lite quote at $T+45$ against Standard at $T+1$ creates a false +15.7% inflation artifact. All quotes must be normalized to standard 15kg economy.
4. **IQR Outlier Boundaries**:
   $$\text{Lower Bound} = \max(1500, Q_1 - 1.5 \times \text{IQR}), \quad \text{Upper Bound} = \min(35000, Q_3 + 2.5 \times \text{IQR})$$
   Filters business class leaks, glitch fares, and negative values.
5. **Sold-Out Flights & Survivorship Bias on $T+1$**:
   When low-cost flights sell out 24 hours prior, only expensive flights remain. Handled via hedonic regression imputation or Carry-Forward Price Indexing to avoid artificial surge distortion.
6. **Non-Stop Strict Filtering**:
   All layovers and 1-stop flights are discarded (`is_non_stop = True` AND `duration <= 240 mins`) because layovers duplicate airport UDF charges and distort sector index pricing.
7. **Paise vs. Rupee Rescaling**:
   Portals like Cleartrip and Goibibo occasionally return fare amounts in integer paise (e.g., `450000` instead of `4500`). Quotes $> 100,000$ on domestic economy routes are automatically divided by 100.
8. **Timezone Trap**:
   Portals running UTC servers misattribute flights departing between 00:00 and 05:30 IST to the previous calendar day. All timestamps strictly enforce `ZoneInfo("Asia/Kolkata")`.

---

## 💾 7. Database & Hosting Roadmap

- **Phase 1 & 2 (Current)**:
  - SQLite 3 database at `database/apix.db` with WAL (Write-Ahead Logging) enabled.
  - Successfully seeded with **5,580 mock quotes** and **31 computed index daily records**.
  - Verified with `manage.py status` and `manage.py audit`.
- **Phase 4 (Cloud Hosting)**:
  - Migration to **Supabase** (Managed PostgreSQL) with zero code refactoring via SQLAlchemy dialect compatibility in `database/db.py`.
  - Credentials stored securely in `.env`.
- **Demo Fail-Safe**:
  - `database/cache/` directory caches JSON snapshots of all 12 routes and computed indices to guarantee 100% demo uptime even if live portal networks drop during the hackathon.

---

## 🔗 8. External Integrations & Tooling
- **Notion Workspace**:
  - Secret: Configured via `NOTION_TOKEN` environment variable.
  - Setup script: `setup_notion_workspace.py` builds databases for Tasks, Portals, Timelines, and Team Roster.
- **Obsidian**:
  - Full project folder acts as an Obsidian vault (`.obsidian/` initialized).
  - Graph connections link all Markdown guides, state files, and timelines.
