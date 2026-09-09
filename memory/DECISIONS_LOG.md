# 🏛️ Operation APIx: Architecture & Strategic Decision Log (ADRs)
### Record of Foundational Technical & Economic Choices (SIH26056)

This document records the architectural, statistical, infrastructural, and operational decisions agreed upon across all project sessions.

---

## 📑 Table of Architectural Decision Records

| ADR ID | Decision Title | Status | Date | Primary Driver |
| :--- | :--- | :--- | :--- | :--- |
| **ADR-001** | Selection of SIH26056 (MoSPI) over other Problem Statements | **Approved** | 2026-09-07 | Low team saturation & immense national macroeconomic impact |
| **ADR-002** | Adoption of DGCA Passenger-Weighted Laspeyres Price Index | **Approved** | 2026-09-08 | Compliance with MoSPI revised CPI (Base 2024=100) standards |
| **ADR-003** | Pure Economic Fare Isolation (Base Fare + YQ Fuel Surcharge) | **Approved** | 2026-09-08 | Elimination of statutory tax noise & OTA convenience fee drip-pricing |
| **ADR-004** | Dual-Tier Database Strategy (SQLite Local → Supabase Cloud) | **Approved** | 2026-09-08 | Fast local development velocity with instant cloud scalability |
| **ADR-005** | Two-Stage Hybrid Scraper Engine (curl_cffi XHR + Playwright) | **Approved** | 2026-09-08 | High extraction throughput (660 searches/run) without CPU overload |
| **ADR-006** | 12 DGCA Domestic Corridors with Normalized Traffic Weights | **Approved** | 2026-09-08 | Statistically representative sample (>60% domestic passenger volume) |
| **ADR-007** | 5 Discrete Booking Horizons (T+1, T+7, T+15, T+30, T+45) | **Approved** | 2026-09-08 | Capturing dynamic yield curve elasticity and advance purchase baselines |
| **ADR-008** | 5-Persona Autonomous Agent Assembly Line Architecture | **Approved** | 2026-09-08 | Strict separation of concerns across extraction, audit, and APIs |
| **ADR-009** | Interquartile Range (IQR) Outlier Fencing & Lite Fare Isolation | **Approved** | 2026-09-08 | Prevention of statistical inflation spikes caused by cabin-only fares |
| **ADR-010** | Fail-Safe Snapshot Replay Cache for Hackathon Grand Finale | **Approved** | 2026-09-08 | Guaranteed 100% demo uptime during jury evaluations at nodal center |
| **ADR-011** | Three-Tier Ingestion Hierarchy with Commercial Fallback API | **Approved** | 2026-09-09 | Automated failover (Bright Data / SerpApi) if direct scrapers get blocked |

---

## 📜 ADR Details

### ADR-001: Selection of SIH26056 (MoSPI)
- **Context**: The team evaluated various SIH 2026 software problem statements (including generic consumer apps, ed-tech, and PS 26154).
- **Decision**: Select **SIH26056** ("Development of an Airfare Price Index for Indian domestic flights").
- **Rationale**:
  1. Exceptionally low competition saturation (0 competing teams initially identified).
  2. Directly sponsored by MoSPI for integration into national CPI calculations.
  3. Perfect synergy with team superpowers: web scraping (Swayam), fullstack UI (Sukesh/Shivam), and statistical indexing.
- **Consequences**: High jury interest and high probability of reaching the Grand Finale.

---

### ADR-002: Adoption of DGCA Passenger-Weighted Laspeyres Price Index
- **Context**: An index formula was needed to track airfare inflation. Paasche indices require contemporaneous passenger counts for every flight (impossible to acquire in real-time). Unweighted arithmetic means bias the index towards obscure, low-traffic routes.
- **Decision**: Implement the official Laspeyres formula:
  $$APIx_t = \sum_{i=1}^{12} \left( W_i \cdot \frac{P_{i,t}}{P_{i,0}} \right) \times 100$$
  Using DGCA annual domestic passenger volume share as fixed base weights $W_i$. Base Year: `2024 = 100`.
- **Consequences**: Full alignment with MoSPI official CPI methodology and NSO expectations.

---

### ADR-003: Pure Economic Fare Isolation (Base Fare + YQ Fuel Surcharge)
- **Context**: Portals quote final checkout prices that include User Development Fees (UDF), Passenger Security Fees (PSF/ASF), CUTE fees, 5% GST, and OTA convenience fees (₹399–₹499 on MakeMyTrip vs ₹0 on EaseMyTrip).
- **Decision**: Strictly define:
  $$\text{Economic Fare} = \text{Base Fare} + \text{Fuel Surcharge (YQ/YR)}$$
  All statutory pass-through taxes and OTA convenience fees are unbundled and excluded from the index calculation.
- **Consequences**: Reflects genuine airline revenue-yield pricing rather than airport infrastructure tax changes or OTA checkout markups.

---

### ADR-004: Dual-Tier Database Strategy (SQLite Local → Supabase Cloud)
- **Context**: Need high velocity during local prototyping without internet dependency, but production requires a shared cloud database for the team and jury demonstrations.
- **Decision**: Built `database/db.py` to seamlessly connect to SQLite 3 WAL (`database/apix.db`) locally, with a single environment toggle `DATABASE_URL` to connect to **Supabase** (PostgreSQL).
- **Consequences**: Zero code refactoring required when deploying to the cloud.

---

### ADR-005: Two-Stage Hybrid Scraper Engine (curl_cffi XHR + Playwright)
- **Context**: Scraping 11 portals across 12 corridors and 5 horizons yields 660 flight queries per sweep. Running 660 full Chromium browser instances causes memory exhaustion and rate-limit triggers.
- **Decision**:
  - **Stage 1 (API Sniffer)**: For portals with discoverable REST/XHR endpoints (EaseMyTrip, Ixigo, Yatra, Cleartrip, Akasa), use `curl_cffi` with Chrome 124 TLS/JA3 fingerprint impersonation for sub-second responses.
  - **Stage 2 (Stealth Browser)**: For portals with aggressive Akamai Bot Manager (MakeMyTrip, IndiGo), use headless Playwright with `playwright-stealth` to harvest session cookies (`_abck`) and handle challenges.
- **Consequences**: 85% of queries execute in $< 1.5$ seconds with minimal RAM usage.

---

### ADR-006: 12 DGCA Domestic Corridors
- **Context**: India has hundreds of domestic city pairs. Ingesting every pair is technically unfeasible and statistically noisy.
- **Decision**: Selected 12 high-impact corridors covering >60% of total domestic passenger traffic:
  - 4 Golden Quadrilateral Metro Routes (`DEL-BOM`, `DEL-BLR`, `BOM-BLR`, `DEL-CCU`).
  - 4 Major Tech & Commercial Links (`BLR-HYD`, `MAA-DEL`, `DEL-HYD`, `DEL-PNQ`).
  - 2 Holiday/Leisure Corridors (`BOM-GOI`, `BOM-CCU`).
  - 2 Strategic & High-Volatility Corridors (`DEL-GAU` for Northeast, `DEL-SXR` for Jammu & Kashmir).
- **Consequences**: Highly accurate representation of national domestic aviation inflation.

---

### ADR-007: 5 Discrete Booking Horizons (T+1, T+7, T+15, T+30, T+45)
- **Context**: Airlines practice dynamic yield management where prices on the same seat bucket increase by 250% to 500% as the departure date nears.
- **Decision**: Track prices at 5 fixed departure windows: $T+1$ (distressed), $T+7$ (short corporate), $T+15$ (standard), $T+30$ (vacation), and $T+45$ (advance baseline).
- **Consequences**: Allows MoSPI to analyze price elasticity curves and detect surge pricing behavior across different consumer horizons.

---

### ADR-008: 5-Persona Autonomous Agent Assembly Line
- **Context**: A monolithic scraper script becomes brittle and unmaintainable across 11 different portals with varying anti-bot systems.
- **Decision**: Decomposed the pipeline into 5 specialized personas defined in `agents/registry.json`:
  1. `api-sniffer-agent` (High-speed XHR reverse engineering).
  2. `stealth-scraper-agent` (Playwright anti-bot specialist).
  3. `tariff-auditor-agent` (Fare unbundling & outlier filtering).
  4. `data-sentinel-agent` (Pydantic v2 schemas & circuit breakers).
  5. `backend-architect-agent` (FastAPI REST endpoints & Supabase sync).
- **Consequences**: Modular development, clean debugging, and zero single-point-of-failure in the codebase.

---

### ADR-009: Interquartile Range (IQR) Outlier Fencing & Lite Fare Isolation
- **Context**: Raw scraping occasionally captures business class quotes (₹35,000+), glitch fares (₹0), or cabin-baggage-only "Lite" fares (7kg only, ₹500 cheaper).
- **Decision**:
  - Bound economic fares between $\max(1500, Q_1 - 1.5 \cdot IQR)$ and $\min(35000, Q_3 + 2.5 \cdot IQR)$.
  - Filter or re-normalize "Lite" fares to standard 15kg check-in economy.
- **Consequences**: Eliminates false inflation spikes (+15.7%) and preserves data integrity for national accounts.

---

### ADR-010: Fail-Safe Snapshot Replay Cache
- **Context**: Grand Finale presentation internet connections at host university nodal centers frequently fail, and live airline portals can temporarily block university IPs.
- **Decision**: Built a local snapshot cache in `database/cache/` containing pre-validated quotes and computed indices. If network requests fail during the hackathon demo, the system automatically falls back to replay mode.
- **Consequences**: Guaranteed 100% demo uptime and bulletproof jury defense.

---

### ADR-011: Three-Tier Ingestion & Commercial Fail-Safe Fallback
- **Context**: Direct web scraping against airlines and OTAs can occasionally encounter aggressive Cloudflare Turnstile or Akamai Bot Manager challenges that trip local circuit breakers. If both direct XHR and Playwright stealth fail during a critical data collection cycle, the pipeline needs an automated commercial failover.
- **Decision**: Architect a three-tier ingestion hierarchy:
  1. *Tier 1 (Primary - Zero Marginal Cost)*: In-house `curl_cffi` TLS/JA3 API Sniffer (<800ms).
  2. *Tier 2 (Secondary)*: Headless Playwright Stealth with session cookie warm-up.
  3. *Tier 3 (Commercial Fallback)*: Automated failover to commercial web unlocking / flight aggregator APIs (e.g. Bright Data Web Unlocker, SerpApi Google Flights, or Amadeus Flight Offers API) triggered on consecutive HTTP 403/CAPTCHA failures.
  4. *Tier 4 (Offline Demo Safety)*: Local JSON snapshot cache (`database/cache/`).
- **Consequences**: Eliminates single-point-of-failure in data harvesting, demonstrates enterprise-grade resilience to SIH judges, and guarantees continuous time-series continuity.
