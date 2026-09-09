-- ==============================================================================
-- OPERATION APIx: Core Relational Database Schema
-- Dialect-Agnostic: 100% compatible with SQLite (local) & PostgreSQL (Supabase)
-- ==============================================================================

-- 1. Representative Routes Table
CREATE TABLE IF NOT EXISTS routes (
    route_id VARCHAR(10) PRIMARY KEY,
    origin_iata VARCHAR(3) NOT NULL,
    origin_city VARCHAR(100) NOT NULL,
    destination_iata VARCHAR(3) NOT NULL,
    destination_city VARCHAR(100) NOT NULL,
    classification VARCHAR(100) NOT NULL,
    weight NUMERIC(6, 4) NOT NULL,
    ps_mandated BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Mandated Ingestion Portals Table (11 Sources)
CREATE TABLE IF NOT EXISTS portals (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'AIRLINE' or 'OTA'
    carrier_code VARCHAR(10),
    domain VARCHAR(100) NOT NULL,
    method VARCHAR(50) NOT NULL, -- 'API_XHR' or 'STEALTH_BROWSER'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Raw Price Quotes Ingestion Table
CREATE TABLE IF NOT EXISTS raw_quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dedup_hash VARCHAR(64) UNIQUE NOT NULL,
    scrape_timestamp TIMESTAMP NOT NULL,
    portal_id VARCHAR(50) NOT NULL,
    carrier_code VARCHAR(10),
    carrier_name VARCHAR(100),
    flight_number VARCHAR(20),
    origin_iata VARCHAR(3) NOT NULL,
    destination_iata VARCHAR(3) NOT NULL,
    departure_time TIMESTAMP,
    arrival_time TIMESTAMP,
    booking_window VARCHAR(10) NOT NULL, -- 'T+1', 'T+7', 'T+15', 'T+30', 'T+45'
    is_non_stop BOOLEAN DEFAULT TRUE,
    base_fare NUMERIC(10, 2),
    fuel_surcharge NUMERIC(10, 2) DEFAULT 0.0,
    taxes_and_fees NUMERIC(10, 2) DEFAULT 0.0,
    convenience_fee NUMERIC(10, 2) DEFAULT 0.0,
    total_fare NUMERIC(10, 2) NOT NULL,
    seats_available INTEGER,
    is_sold_out BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portal_id) REFERENCES portals(id)
);

-- 4. Cleaned & Unbundled Quotes Table (IQR Outlier Filtered)
CREATE TABLE IF NOT EXISTS cleaned_quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_quote_id INTEGER,
    route_id VARCHAR(10) NOT NULL,
    booking_window VARCHAR(10) NOT NULL,
    carrier_code VARCHAR(10) NOT NULL,
    portal_id VARCHAR(50) NOT NULL,
    pure_economic_fare NUMERIC(10, 2) NOT NULL, -- Base Fare + Fuel Surcharge (YQ)
    total_published_fare NUMERIC(10, 2) NOT NULL,
    is_outlier BOOLEAN DEFAULT FALSE,
    outlier_reason VARCHAR(255),
    quote_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (raw_quote_id) REFERENCES raw_quotes(id),
    FOREIGN KEY (route_id) REFERENCES routes(route_id)
);

-- 5. Computed Airfare Price Index (APIx) Time-Series
CREATE TABLE IF NOT EXISTS daily_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    index_date DATE NOT NULL,
    frequency VARCHAR(20) NOT NULL, -- 'DAILY', 'WEEKLY', 'MONTHLY'
    apix_value NUMERIC(8, 2) NOT NULL,
    base_value NUMERIC(8, 2) DEFAULT 100.0,
    inflation_rate_mom NUMERIC(6, 2),
    total_quotes_aggregated INTEGER NOT NULL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Route-Specific Aggregated Indices (For Heatmaps & Elasticity)
CREATE TABLE IF NOT EXISTS route_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    index_date DATE NOT NULL,
    route_id VARCHAR(10) NOT NULL,
    booking_window VARCHAR(10) NOT NULL,
    avg_pure_fare NUMERIC(10, 2) NOT NULL,
    avg_total_fare NUMERIC(10, 2) NOT NULL,
    quotes_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES routes(route_id)
);

-- Indexes for high-speed query performance
CREATE INDEX IF NOT EXISTS idx_raw_quotes_lookup ON raw_quotes(origin_iata, destination_iata, booking_window, scrape_timestamp);
CREATE INDEX IF NOT EXISTS idx_cleaned_quotes_route_date ON cleaned_quotes(route_id, quote_date, booking_window);
CREATE INDEX IF NOT EXISTS idx_daily_index_date ON daily_index(index_date, frequency);
CREATE INDEX IF NOT EXISTS idx_route_index_lookup ON route_index(index_date, route_id, booking_window);
