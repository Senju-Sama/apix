# Findings & Research Log: EaseMyTrip Web Scraping Investigation

## Target Overview
- **Portal**: EaseMyTrip (`easemytrip.com`)
- **Portal Type**: Online Travel Aggregator (OTA)
- **Problem Statement ID**: SIH26056 (MoSPI)
- **Target Test Sector**: `DEL-BOM` (Delhi to Mumbai trunk corridor)
- **Target Horizons**: $T+1$ (Next-day) and $T+7$ (1-week horizon)

---

## Modalities Under Investigation
1. **Modality 1: Direct Internal API / XHR Sniffing**
   - Goal: Direct HTTP query without browser overhead (< 1 second).
   - Tools: `requests`, `curl_cffi` (TLS fingerprint impersonation for Chrome 120/124).
   - Questions: What endpoint generates flight results? Is there a session cookie/token requirement? Does it block standard Python `requests` (403/429) vs `curl_cffi`?

2. **Modality 2: Headless Browser Automation (Playwright)**
   - Goal: Load actual web application in Chromium, handle JS hydration, and parse DOM elements.
   - Tools: `playwright`.
   - Questions: Does EaseMyTrip detect headless Chromium (`navigator.webdriver`)? What are the selector paths for flight cards, airline names, flight numbers, departure times, arrival times, and fares?

3. **Modality 3: Playwright Network Response Interception**
   - Goal: Launch headless browser, but instead of fragile DOM parsing, intercept the background JSON payload directly from the network stream (`page.on('response', ...)`).
   - Questions: Which URL pattern delivers the flight results JSON? Is the JSON clean and unbundled?

4. **Modality 4: Mobile Web / m-site (`m.easemytrip.com`)**
   - Goal: Check if mobile site has simpler DOM, lighter bundle, or unauthenticated REST endpoints.
   - Questions: Does `m.easemytrip.com` exist? How does it behave with mobile User-Agents?

5. **Modality 5: Pre-rendered SEO / Route Schedule Pages**
   - Goal: Check public route landing pages (`easemytrip.com/flights/delhi-to-mumbai-flights.html`).
   - Questions: Do they contain live or static flight fare tables?

---

## Detailed Findings Log

### 1. Modality 1: Direct Internal API / XHR Sniffing (Requests / curl_cffi)
- **Status**: ❌ FAILED for live flight search results.
- **URL Tested**: `https://flight.easemytrip.com/FlightList/Index?srch=DEL-Delhi-India|BOM-Mumbai-India|{DD/MM/YYYY}|1-0-0|E|0|0|0`
- **Result**: HTTP 200 returned, but body is an empty AngularJS Single Page Application (SPA) shell (0 pre-rendered flight rows, 39 unrendered `ng-repeat` directives, `#ResultDiv` hidden).
- **Candidate JSON Endpoints**: `/FlightList/GetFlightList`, `/FlightList/SearchFlight`, etc., on IIS return empty 200 OK (0 bytes).
- **Internal Backend Service**: `POST https://flightservice-node.easemytrip.com/AirAvail_Lights/AirBus_New` requires:
  1. Client-side encrypted token `TKN` produced via AES-128 and `etoken/GIT` + `etoken/GUT`.
  2. AWS WAF token (`tokenAWSWaf` from `challenge.js`).
  3. Google reCAPTCHA Enterprise verification (`recaptcha/enterprise.js`).
- **Conclusion**: Pure HTTP clients without JavaScript engines cannot bypass the multi-stage token handshake for live search.

### 2. Modality 2 & 3: Stealth Playwright Browser & Network Interception
- **Status**: ✅ 100% SUCCESS (Recommended Primary Architecture).
- **Vanilla Playwright**: Immediately blocked by Edge WAF with **HTTP 502 Bad Gateway** (177 bytes) due to `HeadlessChrome` user-agent and `navigator.webdriver = true`.
- **Stealth Playwright Configuration**:
  - Flags: `args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]`
  - Realistic User-Agent: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36`
  - Evasion: `playwright-stealth` applied.
  - Result: **0 blocks, 0 CAPTCHAs, 100% success rate**.
- **Network Interception Endpoint**:
  - `POST https://flightservice-node.easemytrip.com/AirAvail_Lights/AirBus_New`
  - The browser generates the session `TKN` automatically, navigates to the search URL, and triggers `AirBus_New`.
  - Intercepting the response via `page.on("response", ...)` yields the complete **2.35 MB JSON flight inventory** in **~8.98 seconds**.
- **Data Extracted (155 Flights for DEL-BOM)**:
  - Flight identification: Carrier code (`AC`), flight number (`FN`), airline name dictionary (`C`).
  - Schedule: Origin (`OG`), Destination (`DT`), Departure time (`DTM`), Arrival time (`ATM`), Duration (`DUR`), Stops (`STP`).
  - Fare unbundling: Base Fare (`lstFr[0].BF`), Total Taxes & Surcharges (`lstFr[0].TTXMP`), Total Published Fare (`TF` / `PT`).
  - Baggage & policies: Cabin baggage (`fbn`), Check-in baggage (`lstBagg`), cancellation rules (`lstCanPo`).
- **Timing Optimization**: Do NOT wait for `networkidle` (persistent analytics cause 45s timeout). Use `wait_until="domcontentloaded"` and listen for the `AirBus_New` response event.

### 3. Modality 4: Mobile Web & Subdomain Probing
- **Status**: ❌ Mobile subdomain dead; ✅ Main site responsive.
- **`m.easemytrip.com`**: Stale DNS pointing to Google Cloud IP `35.227.238.237` with mismatched SSL certificate (`document-archive-prod.poppankki.net`). Returns 403 Forbidden.
- **Mobile User-Agents**: Sending mobile headers to `www.easemytrip.com` returns the identical responsive AngularJS application.

### 4. Modality 5: Pre-rendered SEO Route Landing Pages
- **Status**: ✅ 100% SUCCESS for macro trends, timetable schedules, and 92-day price indices.
- **Working URL Pattern**: `https://www.easemytrip.com/flights/{origin_city}-{origin_iata}-to-{dest_city}-{dest_iata}/` (e.g. `delhi-del-to-mumbai-bom/`).
- **Access**: Accessible via standard `requests` or `curl_cffi` in **515 ms** with **zero anti-bot friction, no browser, and no tokens**.
- **Data Harvested**:
  - **92-Day Rolling Lowest Fare Calendar**: Complete forward time series from `#fareSlider` (`.fare-item.calendar-date` with `data-date="YYYY-MM-DD"`).
  - **23 Pre-rendered DOM Flight Cards**: `div._owmianbx` with airline, flight numbers, timings, and prices.
  - **Embedded JSON Payload**: `#remainingFlightsData` script tag containing 41 additional flight itineraries with base fare (`ap`) and taxes (`apt`).
- **Limitation**: Renders a fixed benchmark lowest-fare date; cannot serve arbitrary custom-date live queries.


### Modality 1: Direct HTTP Client & XHR Endpoint Investigation (Requests & curl_cffi)
- **Status**: COMPLETE & VERIFIED
- **Script**: `scratch/test_api_client.py` (Structured results in `scratch/test_api_client_results.json`)
- **Key Findings**:
  1. **Homepage Cookie Bootstrap**:
     - `https://www.easemytrip.com` returns HTTP 200 via both standard `requests` (0.55s) and `curl_cffi` Chrome 120 (0.45s).
     - Sets cookies: `{'ccode': 'IN,DELHI', 'CUR_CODE': 'INR', 'lang': 'en-us'}`.
  2. **Search Index Page (`FlightList/Index`) Behavior**:
     - Target URL format: `https://flight.easemytrip.com/FlightList/Index?srch=DEL-Delhi-India|BOM-Mumbai-India|{DD/MM/YYYY}|1-0-0|E|0|0|0`
     - Returns HTTP 200 (454,155 bytes) for both `requests` and `curl_cffi` (with or without cookies).
     - **Critically, the response is pure client-side AngularJS SPA shell**:
       - Contains **0 pre-rendered flight rows** or price values.
       - Contains 39 unrendered `ng-repeat` directives and mustache templates (`{{...}}`).
       - Result container (`#ResultDiv`) has inline style `display:none;`.
       - Multiple loader/spinner components are present (`container_loader`, `#Loader`, `#btnLockPriceLoader`, `#divWebIlusion`).
       - Client-side scripts include **AWS WAF SDK** (`tokenAWSWaf` / `challenge.js`) and **Google reCAPTCHA Enterprise** (`6LeqSKkcAAAAALWU11XjmIIQqT76zFT97OcfqSNR`).
  3. **Candidate Public JSON Endpoints (`flight.easemytrip.com`)**:
     - Tested `GetFlightList`, `GetSearchData`, `SearchFlight`, `GetFlightDetails`, `AirSearch`, `api/FlightList` across GET & POST.
     - **All return HTTP 200 with an empty 0-byte body** (`Content-Type: None`, Server: `Microsoft-IIS/10.0`, `X-AspNetMvc-Version: 5.1`).
     - IIS ASP.NET MVC routes unmatched action names to empty responses; there are **no public REST JSON search endpoints** on `flight.easemytrip.com`.
  4. **Internal Backend Service Sniffing (`flightservice-web.easemytrip.com`)**:
     - Decompiled and reverse-engineered client JavaScript (`SearchJS.js`, `ApiCallLight_new.js`, `Service.js`).
     - EMT generates a search token via an AES-128-CBC encryption handshake (`encKeySrch = "hylW@zmEQdG@4Idr"`):
       - Step 1: `POST https://gi.easemytrip.com/etm/api/etoken/GIT` -> yields identity token `ITK` and IP hash `b`.
       - Step 2: AES encryption -> `POST https://gi.easemytrip.com/etm/api/etoken/GUT` -> yields search token `STK`.
     - When submitting search payload to `POST https://flightservice-web.easemytrip.com/EmtAppService/AirAvail_Lights/AirSearchLightFromCloudKTN_Sec`, the backend returns HTTP 200 with an internal .NET error:
       `"System.IO.FileLoadException: Could not load file or assembly 'Microsoft.IdentityModel.Tokens' ... at WMS.Models.VM.TokenManager.ValidateToken(String token)"`.
     - In real browser sessions, this is combined with dynamic AWS WAF session tokens and reCAPTCHA Enterprise tokens that cannot be maintained reliably in stateless Python HTTP scripts.
  5. **Mobile Surface**:
     - `https://flight.easemytrip.com/FlightList/Index` with iPhone Safari User-Agent returns HTTP 200 (325KB), but is also an AngularJS SPA shell (`ng-repeat`, `#ResultDiv` hidden, loaders active, 0 pre-rendered flights).
  6. **Architectural Recommendation**:
     - **Direct HTTP scraping (via `requests` or `curl_cffi`) cannot be used as the primary data extraction mechanism** because EaseMyTrip is an SPA that loads flight results strictly via browser-evaluated JavaScript, multi-step AES-encrypted token handshakes, AWS WAF, and reCAPTCHA tokens.
     - **Recommendation**: Proceed with **Headless Browser Automation (Playwright)** or **Playwright Network Response Interception** to let the browser execute the full cryptographic and WAF hydration flow, then capture the rendered flight cards or intercept the hydrated flight payload stream.
