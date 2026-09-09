# ✈️ Operation APIx (AFiX)
### Real-Time Airfare Price Index for India through Automated Web Scraping
**Smart India Hackathon 2026** | **Problem Statement ID:** `SIH26056`  
**Sponsoring Ministry:** Ministry of Statistics and Programme Implementation (MoSPI) & NSO  
**Primary Beneficiary:** Reserve Bank of India (RBI) Monetary Policy Committee  
**Theme:** Smart Automation | **Category:** Software  

---

## 🌐 Live Hosted Presentations & Blueprints

Experience the interactive presentations directly in your browser:

- 🎯 **[Live PPT 02: What our Problem Statement is ??](https://senju-sama.github.io/apix/)**  
  *The 6-slide deck framing the national macroeconomic problem and transitioning to the solution architecture.*
- 📊 **[Live PPT 01: Complete 13-Slide Pitch & Team Deck](https://senju-sama.github.io/apix/presentation/PPT_01.html)**  
  *The comprehensive pitch deck including squad breakdown, anti-bot strategies, and 4-week roadmap.*
- 🏛️ **[Interactive System Architecture Blueprint](https://senju-sama.github.io/apix/presentation/architecture.html)**  
  *Deep-dive interactive architecture blueprint detailing data pipelines, database schemas, and API contracts.*
- 📥 **[Download PPT 02 (.pptx)](presentation/PPT_02.pptx)**  
  *Microsoft PowerPoint presentation format.*

---

## 🧭 Executive Summary: What our Problem Statement is

### 1. The Reality Check
In 2026, the Government of India measures airfare inflation by sending physical surveyors into airline booking counters with paper clipboards once a month. Meanwhile, over **92% of domestic flight tickets** are purchased online, where algorithmic dynamic pricing swings **200% to 400%** daily based on departure proximity, seat capacity, and seasonal surges.

### 2. The Price Disconnect
- **Monthly Paper Survey:** ₹4,500 *(static counter fare recorded once a month in New Delhi)*
- **Live Online Market:** ₹16,800 *(+273% festival surge at T+1 Day)*

### 3. The Macroeconomic Stakes
Under India's **Flexible Inflation Targeting** mandate, the RBI MPC must keep CPI inflation at 4% (±2%). When airfares are mismeasured or lagged by weeks, the Transport & Communication basket distorts headline inflation—leading to delayed or mistimed national interest rate revisions.

### 4. The Official Mandate
Under the **CPI Series (Base 2024=100)** revision, MoSPI officially mandated shifting from manual surveyor visits to **automated web scraping** for volatile services like civil aviation. MoSPI posted **SIH26056** because they require a sovereign, automated software platform to execute this mandate.

---

## 🚀 Let's Move to Soln: 3-Pillar Engineering Architecture

Operation APIx replaces this multi-billion rupee economic blind spot across three integrated pillars:

```
┌────────────────────────────────────────────────────────┐
│   01 • AUTOMATED SCRAPING ENGINE                       │
│   Stealth Playwright + Direct OTA JSON API Bridges     │
│   Tracks Top 15 Routes × 5 Booking Horizons (T+1..T+45)│
└──────────────────────────┬─────────────────────────────┘
                           │ Daily Fare Feeds
┌──────────────────────────▼─────────────────────────────┐
│   02 • LASPEYRES ECONOMETRIC COMPUTE ENGINE            │
│   Pure Base-Fare Unbundling (Excluding GST/UDF)        │
│   IQR Outlier Cleaning + DGCA Monthly Passenger Weights│
└──────────────────────────┬─────────────────────────────┘
                           │ Sub-second Index Aggregation
┌──────────────────────────▼─────────────────────────────┐
│   03 • SOVEREIGN MoSPI & RBI COMMAND CENTER            │
│   Real-time Inflation Gauges, Flight Corridor Maps     │
│   Automated Anomaly Detection & Secure REST APIs       │
└────────────────────────────────────────────────────────┘
```

---

## 📂 Repository Structure

```
├── presentation/
│   ├── PPT_02.html          # PPT 2: Problem Statement & Transition Deck (6 slides)
│   ├── PPT_02.pptx          # PowerPoint PPT 2 file
│   ├── PPT_01.html          # PPT 1: Full 13-slide pitch deck
│   ├── architecture.html    # Interactive System Architecture visualizer
│   └── SIH2026_PPT_MULTI_AGENT_SYNTHESIS.md
├── scrapers/                # Web scraping and OTA ingestion engines
├── engine/                  # Laspeyres economic index compute engine
├── database/                # Schema definitions, migrations, and mock data
├── pipeline/                # Anomaly detection and data validation sentinels
├── backend/                 # FastAPI REST API endpoints
├── index.html               # Web portal redirecting to PPT 02
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 💻 Local Setup & Development

### 1. Clone the Repository
```bash
git clone https://github.com/Senju-Sama/apix.git
cd apix
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Open Presentations
Simply double click or open `index.html` or `presentation/PPT_02.html` in any modern web browser.
- Press **`Space`** or **`→`** for next slide
- Press **`←`** for previous slide
- Press **`P`** for speaker notes and presentation timer
- Press **`F`** for fullscreen presentation mode

---

## 📜 License
Developed for the **Smart India Hackathon 2026**. Sovereign GovTech architecture for MoSPI & the Reserve Bank of India.
