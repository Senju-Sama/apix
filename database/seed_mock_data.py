import random
import sys
from datetime import datetime, timedelta, date
from pathlib import Path

# Ensure project root is in Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import CONFIG_DIR
from database.db import get_engine, init_db
from pipeline.models import RawFlightQuote, FareBreakdown, CleanedFlightQuote
from sqlalchemy import text
import json

AIRLINES = [
    {"code": "6E", "name": "IndiGo"},
    {"code": "AI", "name": "Air India"},
    {"code": "IX", "name": "Air India Express"},
    {"code": "QP", "name": "Akasa Air"},
    {"code": "SG", "name": "SpiceJet"},
]

PORTALS = ["easemytrip", "ixigo", "makemytrip", "yatra", "indigo", "airindia"]

BASE_PRICES = {
    "DEL-BOM": 4200,
    "DEL-BLR": 4800,
    "BOM-BLR": 3600,
    "DEL-CCU": 4500,
    "BLR-HYD": 2800,
    "MAA-DEL": 4700,
    "DEL-HYD": 4100,
    "BOM-GOI": 3200,
    "DEL-PNQ": 3900,
    "BOM-CCU": 4900,
    "DEL-GAU": 5400,
    "DEL-SXR": 5200,
}

WINDOW_SURGE_MULTIPLIERS = {
    "T+45": 1.00,  # Baseline
    "T+30": 1.08,  # Standard planned
    "T+15": 1.25,  # Mid-range
    "T+7":  1.60,  # Short notice
    "T+1":  2.35,  # Last-minute surge
}

def seed_mock_quotes(days_back: int = 30):
    """Generates realistic calibrated historical flight quotes for testing and offline demo."""
    init_db()
    engine = get_engine()

    # Load routes and windows
    with open(CONFIG_DIR / "routes.json", "r", encoding="utf-8") as f:
        routes = json.load(f)
    with open(CONFIG_DIR / "windows.json", "r", encoding="utf-8") as f:
        windows = json.load(f)

    today = date.today()
    total_raw = 0
    total_cleaned = 0

    print(f"Generating realistic dataset over past {days_back} days...")

    with engine.begin() as conn:
        # Clear previous quotes if any
        conn.execute(text("DELETE FROM cleaned_quotes"))
        conn.execute(text("DELETE FROM raw_quotes"))

        for d in range(days_back, -1, -1):
            scrape_date = today - timedelta(days=d)
            daily_quotes = []

            for route in routes:
                route_id = route["route_id"]
                origin, dest = route["origin_iata"], route["destination_iata"]
                anchor_base = BASE_PRICES.get(route_id, 4000)

                # Add a seasonal/time drift over the 30-day window
                drift_factor = 1.0 + (0.003 * (30 - d)) + random.uniform(-0.04, 0.04)

                for win in windows:
                    w_id = win["window_id"]
                    surge = WINDOW_SURGE_MULTIPLIERS.get(w_id, 1.0)

                    # Generate 2 to 3 flights per airline for this route/window
                    for airline in random.sample(AIRLINES, k=3):
                        portal = random.choice(PORTALS)
                        flight_num = f"{airline['code']}-{random.randint(1001, 9999)}"

                        # Compute fare breakdown
                        raw_base = anchor_base * surge * drift_factor * random.uniform(0.92, 1.10)
                        base_fare = round(raw_base, 2)
                        fuel_yq = round(base_fare * random.uniform(0.08, 0.12), 2)
                        udf_psf = round(random.choice([650, 780, 920, 1100]), 2)
                        gst = round((base_fare + fuel_yq) * 0.05, 2)
                        taxes_fees = round(udf_psf + gst, 2)
                        conv_fee = 350.0 if portal in ["makemytrip", "yatra", "ixigo"] else 0.0
                        total_fare = round(base_fare + fuel_yq + taxes_fees + conv_fee, 2)

                        # Create Pydantic validated quote
                        quote = RawFlightQuote(
                            scrape_timestamp=datetime.combine(scrape_date, datetime.min.time()) + timedelta(hours=random.randint(6, 22)),
                            portal_id=portal,
                            carrier_code=airline["code"],
                            carrier_name=airline["name"],
                            flight_number=flight_num,
                            origin_iata=origin,
                            destination_iata=dest,
                            departure_time=datetime.combine(scrape_date + timedelta(days=win["days_ahead"]), datetime.min.time()) + timedelta(hours=random.randint(6, 21)),
                            booking_window=w_id,
                            is_non_stop=True,
                            fare=FareBreakdown(
                                base_fare=base_fare,
                                fuel_surcharge=fuel_yq,
                                taxes_and_fees=taxes_fees,
                                convenience_fee=conv_fee,
                                total_fare=total_fare
                            ),
                            seats_available=random.randint(1, 9),
                            is_sold_out=False
                        )

                        # Insert into raw_quotes
                        res = conn.execute(
                            text("""
                                INSERT INTO raw_quotes (
                                    dedup_hash, scrape_timestamp, portal_id, carrier_code, carrier_name,
                                    flight_number, origin_iata, destination_iata, departure_time,
                                    booking_window, is_non_stop, base_fare, fuel_surcharge,
                                    taxes_and_fees, convenience_fee, total_fare, seats_available, is_sold_out
                                ) VALUES (
                                    :dedup_hash, :scrape_timestamp, :portal_id, :carrier_code, :carrier_name,
                                    :flight_number, :origin_iata, :destination_iata, :departure_time,
                                    :booking_window, :is_non_stop, :base_fare, :fuel_surcharge,
                                    :taxes_and_fees, :convenience_fee, :total_fare, :seats_available, :is_sold_out
                                )
                            """),
                            {
                                "dedup_hash": quote.dedup_hash,
                                "scrape_timestamp": quote.scrape_timestamp,
                                "portal_id": quote.portal_id,
                                "carrier_code": quote.carrier_code,
                                "carrier_name": quote.carrier_name,
                                "flight_number": quote.flight_number,
                                "origin_iata": quote.origin_iata,
                                "destination_iata": quote.destination_iata,
                                "departure_time": quote.departure_time,
                                "booking_window": quote.booking_window,
                                "is_non_stop": quote.is_non_stop,
                                "base_fare": quote.fare.base_fare,
                                "fuel_surcharge": quote.fare.fuel_surcharge,
                                "taxes_and_fees": quote.fare.taxes_and_fees,
                                "convenience_fee": quote.fare.convenience_fee,
                                "total_fare": quote.fare.total_fare,
                                "seats_available": quote.seats_available,
                                "is_sold_out": quote.is_sold_out
                            }
                        )
                        raw_id = res.lastrowid
                        total_raw += 1

                        # Populate Cleaned Quote (Unbundled Pure Fare)
                        pure_fare = round(base_fare + fuel_yq, 2)
                        conn.execute(
                            text("""
                                INSERT INTO cleaned_quotes (
                                    raw_quote_id, route_id, booking_window, carrier_code, portal_id,
                                    pure_economic_fare, total_published_fare, is_outlier, quote_date
                                ) VALUES (
                                    :raw_quote_id, :route_id, :booking_window, :carrier_code, :portal_id,
                                    :pure_economic_fare, :total_published_fare, :is_outlier, :quote_date
                                )
                            """),
                            {
                                "raw_quote_id": raw_id,
                                "route_id": route_id,
                                "booking_window": w_id,
                                "carrier_code": airline["code"],
                                "portal_id": portal,
                                "pure_economic_fare": pure_fare,
                                "total_published_fare": total_fare,
                                "is_outlier": False,
                                "quote_date": scrape_date
                            }
                        )
                        total_cleaned += 1

    print(f"Successfully seeded {total_raw:,} raw quotes and {total_cleaned:,} cleaned quotes over {days_back} days.")

if __name__ == "__main__":
    seed_mock_quotes(days_back=30)
