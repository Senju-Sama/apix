# 📜 SIH26056: Master Project Charter & Single Source of Truth
### Ministry of Statistics and Programme Implementation (MoSPI) | DIID
**Project**: Development of a Real-time Airfare Price Index for India through Automated Web Scraping  
**Problem Statement ID**: `SIH26056` | **Category**: Software | **Theme**: Smart Automation  
**Target Consumer**: National Statistical Office (NSO) & Reserve Bank of India (RBI)  
**Dataset Reference**: [MoSPI eSankhyiki Portal](https://esankhyiki.mospi.gov.in)

---

> [!IMPORTANT]
> **PERMANENT SYSTEM INSTRUCTION FOR ALL AGENTS & SESSIONS:**  
> This file is the **absolute, non-negotiable reference** for this project. No agent, script, or contributor shall make assumptions that contradict the explicit mandates set forth in this document. Every data pipeline, scraper, math engine, and UI component must align directly with the specifications below.

---

## 1. Verbatim Problem Statement (MoSPI Official Text)

### Background:
The Consumer Price Index (CPI) released by the National Statistical Office (NSO), Ministry of Statistics and Programme Implementation (MoSPI), is the primary measure of retail inflation in India and is used by the Reserve Bank of India (RBI) for setting monetary policy under the flexible inflation-targeting framework. The current CPI framework, however, collects 'Transport and Communication' sub-group prices, including air travel fares, primarily through manual price-collection from a limited set of outlets and ticketing offices. With over 90% of domestic air tickets in India now sold online through airline websites and Online Travel Aggregators (OTAs) such as MakeMyTrip, Yatra, EaseMyTrip, Cleartrip, Ixigo and Goibibo, manual collection no longer captures the highly dynamic, route-specific, and time-sensitive pricing that Indian consumers actually face. Airfares in India follow dynamic pricing where the same sector can vary by 200-400% within a single day depending on advance-booking window, day-of-week, demand surges, festival seasons and fuel-price-linked surcharges. There is therefore an urgent need for an automated, scalable and high-frequency data-collection system that mirrors what a real Indian traveller pays.

### Detailed Description:
The problem statement envisages development of an end-to-end software platform that automatically web-scrapes airfare data from major Indian airline websites (**IndiGo, Air India, Air India Express, Akasa Air, SpiceJet**) and leading OTAs (**MakeMyTrip, Yatra, EaseMyTrip, Cleartrip, Ixigo and Goibibo**), cleans and normalises the collected price quotes, and computes a Real-time Airfare Price Index (APIx) at **daily, weekly and monthly frequencies**. The system shall maintain a basket of representative city-pairs (such as **DEL-BOM, DEL-BLR, BOM-BLR, DEL-CCU, BLR-HYD, MAA-DEL, etc.**) selected on the basis of DGCA passenger-traffic data, and shall capture fares for multiple advance-purchase windows (**T+1, T+7, T+15, T+30, T+45 days**). Scraping must handle **JavaScript-rendered pages, dynamic CAPTCHAs, anti-bot measures, IP rotation, and session management** while remaining compliant with the robots.txt and terms of service of source websites, with appropriate rate-limiting and ethical-scraping safeguards. The collected raw quotes shall be passed through a data-cleaning pipeline that **removes outliers, handles missing values, accounts for cancellations/sold-out flights, and separates base fare from taxes, user-development fee and convenience charges**. The dashboard must visualise price trends, sector-wise heatmaps, lead-time elasticity curves, and provide an API that the NSO and RBI can consume.

### Expected Solution:
A working software prototype consisting of:
1. A robust, ethically-designed multi-source web-scraping engine using Python (Scrapy/Selenium/Playwright) capable of scheduled daily extraction from airline portals.
2. A cleaned and de-duplicated airfare database with metadata such as origin, destination, carrier, advance-purchase window, fare-class, base fare, taxes and total fare.
3. An index-construction module based on PSD given routes and weights.
4. A web-based interactive dashboard showing the daily Airfare Price Index.
5. Documentation, automated testing, and demonstration of at least **30 days of back-tested results against publicly available DGCA monthly average-fare data**.

---

## 2. The 11 Mandated Data Sources

Every source listed below is explicitly named in the problem statement. The system architecture uses a unified adapter interface (`BaseScraper`) for all 11 sources:

| Source Type | Entity Name | Portal Domain | Scraping Role |
| :--- | :--- | :--- | :--- |
| **Airline (Carrier)** | **IndiGo** | `goindigo.in` | Market leader (~61% traffic share); baseline fare unbundling. |
| **Airline (Carrier)** | **Air India** | `airindia.com` | Full-service carrier pricing and baggage-bundled fare classes. |
| **Airline (Carrier)** | **Air India Express**| `airindiaexpress.com` | Budget carrier pricing across secondary corridors. |
| **Airline (Carrier)** | **Akasa Air** | `akasaair.com` | Fast-growing LCC dynamic yield monitoring. |
| **Airline (Carrier)** | **SpiceJet** | `spicejet.com` | Domestic LCC routes and regional connectivity schemes. |
| **OTA (Aggregator)** | **MakeMyTrip** | `makemytrip.com` | Largest retail volume OTA; market-wide retail consumer pricing. |
| **OTA (Aggregator)** | **EaseMyTrip** | `easemytrip.com` | Zero convenience fee model; structured internal JSON responses. |
| **OTA (Aggregator)** | **Yatra** | `yatra.com` | Corporate & retail split ticket pricing. |
| **OTA (Aggregator)** | **Cleartrip** | `cleartrip.com` | Flipkart ecosystem pricing and dynamic cashback/discounts. |
| **OTA (Aggregator)** | **Ixigo** | `ixigo.com` | High-frequency AI fare prediction aggregator. |
| **OTA (Aggregator)** | **Goibibo** | `goibibo.com` | Budget/youth segment retail ticket pricing. |

---

## 3. Representative City-Pair Basket (DGCA Passenger Traffic)

Selected based on official DGCA monthly domestic traffic statistics ($W_i$ = Route Passenger Weight):

| Sector Code | Origin Airport | Destination Airport | Classification | Weight ($W_i$) |
| :--- | :--- | :--- | :--- | :---: |
| **`DEL-BOM`** | Delhi (DEL) | Mumbai (BOM) | *Mandated in PS* - Heavy Metro Trunk | 0.142 |
| **`DEL-BLR`** | Delhi (DEL) | Bengaluru (BLR) | *Mandated in PS* - Heavy Metro Trunk | 0.098 |
| **`BOM-BLR`** | Mumbai (BOM) | Bengaluru (BLR) | *Mandated in PS* - Metro High-Density | 0.065 |
| **`DEL-CCU`** | Delhi (DEL) | Kolkata (CCU) | *Mandated in PS* - Metro East Trunk | 0.054 |
| **`BLR-HYD`** | Bengaluru (BLR) | Hyderabad (HYD) | *Mandated in PS* - Short-Haul Tech Hub | 0.042 |
| **`MAA-DEL`** | Chennai (MAA) | Delhi (DEL) | *Mandated in PS* - North-South Trunk | 0.038 |
| **`DEL-HYD`** | Delhi (DEL) | Hyderabad (HYD) | High-Density Metro Corridor | 0.051 |
| **`BOM-GOI`** | Mumbai (BOM) | Goa (GOI/GOX) | High-Volatility Leisure / Holiday Surge | 0.039 |
| **`DEL-PNQ`** | Delhi (DEL) | Pune (PNQ) | Tier-1 to Tier-2 Corporate Hub | 0.028 |
| **`BOM-CCU`** | Mumbai (BOM) | Kolkata (CCU) | West-East Commercial Corridor | 0.026 |
| **`DEL-GAU`** | Delhi (DEL) | Guwahati (GAU) | Northeast Regional Lifeline | 0.021 |
| **`DEL-SXR`** | Delhi (DEL) | Srinagar (SXR) | High-Altitude Seasonal Tourist Corridor | 0.018 |

---

## 4. Advance Purchase Windows (Mandated by MoSPI)

For each route, the system must collect quotes across all 5 horizons:
1. **$T+1$ Day**: Last-minute / emergency travel (measures peak price gouging & dynamic surge).
2. **$T+7$ Days**: Short-notice / business travel.
3. **$T+15$ Days**: Mid-range booking window.
4. **$T+30$ Days**: Standard advance consumer planning baseline.
5. **$T+45$ Days**: Early-bird leisure baseline before seat buckets (RBDs) deplete.

---

## 5. Mandatory Fare Unbundling Schema

Raw prices must be decomposed to isolate genuine airline pricing power from statutory charges:

$$\text{Total Published Fare} = \text{Base Fare} + \text{Airline Fuel/Carrier Surcharge (YQ/YR)} + \text{Statutory Taxes (GST)} + \text{Airport Fees (UDF + PSF + ASF)} + \text{OTA Convenience Fee}$$

* **Pure Economic Variable (CPI Input)**: $\text{Base Fare} + \text{Carrier Surcharge (YQ)}$
* **Statutory Taxes & Fees**: GST (5% Economy), User Development Fee (UDF), Passenger Service Fee (PSF), Aviation Security Fee (ASF).
* **Intermediary Fee**: OTA convenience fee (must be filtered out to avoid double counting).

---

## 6. Calculation Frequencies & Mathematical Model

The system outputs three index frequencies:
1. **Daily Index ($\text{APIx}_{\text{daily}}$)**: Computed from the 00:30 AM standardized baseline run.
2. **Weekly Index ($\text{APIx}_{\text{weekly}}$)**: 7-day rolling weighted geometric mean.
3. **Monthly Index ($\text{APIx}_{\text{monthly}}$)**: Aggregated calendar-month index for direct MoSPI CPI integration.

### Index Formula (Laspeyres Price Index):
$$\text{APIx}_t = \sum_{i=1}^{n} \left( \frac{P_{i,t}}{P_{i,0}} \times W_i \right) \times 100$$
Where:
* $P_{i,t}$ = Trimmed median price for route $i$ at time $t$ across all valid flight quotes.
* $P_{i,0}$ = Base period price for route $i$ (calibrated from Base 2024 = 100).
* $W_i$ = DGCA traffic volume weight for route $i$ ($\sum W_i = 1.0$).

---

## 7. Mandatory Validation: 30-Day DGCA Backtesting

The solution must cross-validate computed index numbers against:
- **Source**: DGCA Monthly Domestic Air Tariff & Passenger Reports from `esankhyiki.mospi.gov.in`.
- **Validation Metric**: Mean Absolute Percentage Error (MAPE) between $\text{APIx}_{\text{monthly}}$ and DGCA official monthly average sector fares must be $\le 5\%$.
