"""
Operation APIx: EaseMyTrip Scraper Adapter (SIH26056)
Single Source of Truth: SIH26056_PROJECT_CHARTER.md & scrapers/SCRAPING_RESEARCH_AND_RUNBOOK.md

Extracts live flight quotes and decomposed fare structures (Base Fare + Taxes)
from EaseMyTrip using Stealth Playwright Network Response Interception.
"""

import asyncio
import re
import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from pipeline.models import RawFlightQuote, FareBreakdown
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger("apix.scrapers.easemytrip")

# Mapping of IATA codes to city names used in EaseMyTrip search URLs
IATA_CITY_MAP = {
    "DEL": "Delhi",
    "BOM": "Mumbai",
    "BLR": "Bengaluru",
    "CCU": "Kolkata",
    "HYD": "Hyderabad",
    "MAA": "Chennai",
    "GOI": "Goa",
    "PNQ": "Pune",
    "GAU": "Guwahati",
    "SXR": "Srinagar",
}

class EaseMyTripScraper(BaseScraper):
    """
    EaseMyTrip Scraping Adapter.
    Uses Stealth Playwright with background network response interception (`AirBus_New`)
    to reliably harvest live domestic flight quotes without DOM selector fragility.
    """

    def __init__(self, rate_limit_delay: float = 2.0, timeout_seconds: float = 30.0):
        super().__init__(
            portal_id="easemytrip",
            portal_name="EaseMyTrip",
            base_url="https://flight.easemytrip.com",
            rate_limit_delay=rate_limit_delay,
            timeout_seconds=timeout_seconds,
        )

    def _build_search_url(self, origin_iata: str, destination_iata: str, dep_date: date) -> str:
        """Constructs EaseMyTrip direct search URL format."""
        orig_city = IATA_CITY_MAP.get(origin_iata, origin_iata)
        dest_city = IATA_CITY_MAP.get(destination_iata, destination_iata)
        date_str = dep_date.strftime("%d/%m/%Y")
        
        return (
            f"https://flight.easemytrip.com/FlightList/Index?"
            f"srch={origin_iata}-{orig_city}-India|{destination_iata}-{dest_city}-India|{date_str}"
            f"&px=1-0-0&cbn=0&ar=e&isow=true&isrd=false&lang=en-us&isct=false"
        )

    async def _async_intercept_airbus(self, search_url: str) -> Optional[Dict[str, Any]]:
        """
        Executes stealth browser session, navigates directly to search URL,
        and intercepts the raw AirBus_New pricing engine JSON.
        """
        captured_data: Optional[Dict[str, Any]] = None

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            await Stealth().apply_stealth_async(page)

            async def handle_response(response):
                nonlocal captured_data
                if "AirBus_New" in response.url and response.status == 200:
                    try:
                        captured_data = await response.json()
                    except Exception as err:
                        logger.warning(f"[EaseMyTrip] Failed to decode AirBus_New JSON: {err}")

            page.on("response", handle_response)

            try:
                # Use domcontentloaded: do not wait for networkidle (EMT has persistent tracking sockets)
                await page.goto(search_url, wait_until="domcontentloaded", timeout=int(self.timeout_seconds * 1000))
                
                # Poll for the background pricing response (arrives within 5-9 seconds)
                max_iterations = int((self.timeout_seconds - 5) * 2)
                for _ in range(max(10, max_iterations)):
                    if captured_data is not None:
                        break
                    await page.wait_for_timeout(500)

            except Exception as e:
                logger.error(f"[EaseMyTrip] Playwright navigation error: {e}")
            finally:
                await browser.close()

        return captured_data

    def _parse_airbus_payload(
        self,
        payload: Dict[str, Any],
        origin_iata: str,
        destination_iata: str,
        booking_window: str,
        target_date: date,
    ) -> List[RawFlightQuote]:
        """
        Parses raw AirBus_New JSON payload into validated RawFlightQuote domain objects.
        """
        quotes: List[RawFlightQuote] = []
        now = datetime.now()

        airline_dict = payload.get("C", {})  # e.g. {"6E": "IndiGo", "AI": "Air India"}
        flight_details_dict = payload.get("dctFltDtl", {})
        journeys = payload.get("j", [])
        if not journeys or not isinstance(journeys, list):
            return quotes

        first_journey = journeys[0]
        segments = first_journey.get("s", [])

        for seg in segments:
            b_list = seg.get("b", [])
            for b_item in b_list:
                fl_indices = b_item.get("FL", [])
                if not fl_indices:
                    continue

                # Multi-leg handling: inspect first leg for primary carrier/departure
                first_leg_idx = str(fl_indices[0])
                first_leg = flight_details_dict.get(first_leg_idx)
                if not first_leg:
                    continue

                # Last leg for arrival time
                last_leg_idx = str(fl_indices[-1])
                last_leg = flight_details_dict.get(last_leg_idx, first_leg)

                carrier_code = first_leg.get("AC")
                flight_num = first_leg.get("FN")
                carrier_name = airline_dict.get(carrier_code, carrier_code)
                full_flight_code = f"{carrier_code}-{flight_num}" if carrier_code and flight_num else None

                # Non-stop determination
                stop_count = int(b_item.get("BDT", 0)) if str(b_item.get("BDT", 0)).isdigit() else len(fl_indices) - 1
                is_non_stop = (stop_count == 0)

                # Departure & Arrival datetimes
                dept_time_str = first_leg.get("DTM", "00:00")
                arr_time_str = last_leg.get("ATM", "00:00")
                
                try:
                    dept_dt = datetime.combine(
                        target_date,
                        datetime.strptime(dept_time_str, "%H:%M").time()
                    )
                except ValueError:
                    dept_dt = None

                try:
                    arr_dt = datetime.combine(
                        target_date,
                        datetime.strptime(arr_time_str, "%H:%M").time()
                    )
                    # If arrival is earlier than departure, flight arrived next day
                    if dept_dt and arr_dt < dept_dt:
                        arr_dt += timedelta(days=1)
                except ValueError:
                    arr_dt = None

                # Fare Unbundling (Stored on seg level in AirBus_New)
                total_fare = float(seg.get("TF") or seg.get("PT") or b_item.get("TF") or b_item.get("PT") or 0.0)
                base_fare = 0.0
                taxes = 0.0

                lst_fares = seg.get("lstFr") or b_item.get("lstFr", [])
                if lst_fares and isinstance(lst_fares, list):
                    first_fare_tier = lst_fares[0]
                    base_fare = float(first_fare_tier.get("BF") or 0.0)
                    taxes = float(first_fare_tier.get("TTXMP") or 0.0)

                if base_fare <= 0.0:
                    # Fallback approximation: 70% base fare, 30% statutory taxes
                    base_fare = round(total_fare * 0.70, 2)
                    taxes = round(total_fare - base_fare, 2)

                # Convenience fee: EaseMyTrip search displays 0 INR convenience fee
                fare_breakdown = FareBreakdown(
                    base_fare=base_fare,
                    fuel_surcharge=0.0,
                    taxes_and_fees=taxes,
                    convenience_fee=0.0,
                    total_fare=total_fare,
                )

                try:
                    quote = RawFlightQuote(
                        scrape_timestamp=now,
                        portal_id=self.portal_id,
                        carrier_code=carrier_code,
                        carrier_name=carrier_name,
                        flight_number=full_flight_code,
                        origin_iata=origin_iata,
                        destination_iata=destination_iata,
                        departure_time=dept_dt,
                        arrival_time=arr_dt,
                        booking_window=booking_window,
                        is_non_stop=is_non_stop,
                        fare=fare_breakdown,
                        seats_available=None,
                        is_sold_out=False,
                    )
                    quotes.append(quote)
                except Exception as val_err:
                    logger.warning(f"[EaseMyTrip] Validation error on quote: {val_err}")

        return quotes

    def scrape_route(
        self,
        origin_iata: str,
        destination_iata: str,
        booking_window: str,
        departure_date: Optional[date] = None,
    ) -> List[RawFlightQuote]:
        """
        Synchronous entry point that invokes the async Playwright interceptor
        and parses flight quotes for a specified route and horizon.
        """
        target_date = departure_date or self.calculate_departure_date(booking_window)
        search_url = self._build_search_url(origin_iata, destination_iata, target_date)
        
        logger.info(f"[EaseMyTrip] Querying {origin_iata}-{destination_iata} for {booking_window} ({target_date})...")
        
        payload = asyncio.run(self._async_intercept_airbus(search_url))
        if not payload:
            raise RuntimeError(f"[EaseMyTrip] Failed to capture AirBus_New response payload for {search_url}")

        quotes = self._parse_airbus_payload(
            payload=payload,
            origin_iata=origin_iata,
            destination_iata=destination_iata,
            booking_window=booking_window,
            target_date=target_date,
        )
        logger.info(f"[EaseMyTrip] Successfully extracted {len(quotes)} flight quotes ({sum(1 for q in quotes if q.is_non_stop)} non-stop).")
        return quotes
