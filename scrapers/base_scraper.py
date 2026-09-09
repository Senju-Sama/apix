"""
Operation APIx: Base Scraper Abstract Class (SIH26056)
Single Source of Truth: SIH26056_PROJECT_CHARTER.md

Unified adapter interface for all 11 mandated Indian airline and OTA portals:
- Airlines: IndiGo, Air India, Air India Express, Akasa Air, SpiceJet
- OTAs: EaseMyTrip, MakeMyTrip, Ixigo, Yatra, Cleartrip, Goibibo
"""

import abc
import random
import time
import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any

from pipeline.models import RawFlightQuote, FareBreakdown

logger = logging.getLogger("apix.scrapers.base")

WINDOW_DAYS_MAP = {
    "T+1": 1,
    "T+7": 7,
    "T+15": 15,
    "T+30": 30,
    "T+45": 45,
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

class BaseScraper(abc.ABC):
    """
    Abstract Base Class for all Operation APIx Web Scraper Adapters.
    Enforces standardized contract, ethical rate-limiting, and Pydantic validation.
    """

    def __init__(
        self,
        portal_id: str,
        portal_name: str,
        base_url: str,
        rate_limit_delay: float = 2.0,
        timeout_seconds: float = 25.0,
    ):
        self.portal_id = portal_id
        self.portal_name = portal_name
        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self.timeout_seconds = timeout_seconds
        self._last_request_time: float = 0.0
        self.error_count: int = 0
        self.is_circuit_open: bool = False

    def get_random_user_agent(self) -> str:
        """Returns a randomized modern desktop user-agent."""
        return random.choice(USER_AGENTS)

    def calculate_departure_date(self, booking_window: str, base_date: Optional[date] = None) -> date:
        """
        Converts MoSPI booking horizon (T+1, T+7, T+15, T+30, T+45) into a target departure date.
        """
        if booking_window not in WINDOW_DAYS_MAP:
            raise ValueError(f"Unknown booking window: {booking_window}. Expected one of {list(WINDOW_DAYS_MAP.keys())}")
        
        anchor = base_date or date.today()
        days = WINDOW_DAYS_MAP[booking_window]
        return anchor + timedelta(days=days)

    def enforce_rate_limit(self) -> None:
        """
        Ethical scraping delay with randomized Gaussian jitter (+-20%) to avoid burst traffic.
        """
        now = time.time()
        elapsed = now - self._last_request_time
        jitter = random.uniform(0.8, 1.2)
        required_delay = self.rate_limit_delay * jitter

        if elapsed < required_delay:
            sleep_duration = required_delay - elapsed
            time.sleep(sleep_duration)

        self._last_request_time = time.time()

    def record_success(self) -> None:
        """Resets consecutive error counter on successful extraction."""
        self.error_count = 0
        self.is_circuit_open = False

    def record_failure(self, error: Exception) -> None:
        """Increments error counter and trips circuit breaker if threshold exceeded."""
        self.error_count += 1
        logger.warning(f"[{self.portal_name}] Extraction error #{self.error_count}: {error}")
        if self.error_count >= 5:
            self.is_circuit_open = True
            logger.error(f"[{self.portal_name}] Circuit breaker TRIPPED! Disabling adapter temporarily.")

    @abc.abstractmethod
    def scrape_route(
        self,
        origin_iata: str,
        destination_iata: str,
        booking_window: str,
        departure_date: Optional[date] = None,
    ) -> List[RawFlightQuote]:
        """
        Extracts raw flight quotes for a single origin-destination city pair and booking window.
        Must return validated RawFlightQuote objects conforming to pipeline/models.py.
        """
        pass

    def scrape_all_windows(
        self,
        origin_iata: str,
        destination_iata: str,
        base_date: Optional[date] = None,
    ) -> List[RawFlightQuote]:
        """
        Convenience runner across all 5 MoSPI mandated booking windows:
        T+1, T+7, T+15, T+30, T+45.
        """
        all_quotes: List[RawFlightQuote] = []
        for window in ["T+1", "T+7", "T+15", "T+30", "T+45"]:
            if self.is_circuit_open:
                logger.warning(f"[{self.portal_name}] Circuit is open. Skipping {window} on {origin_iata}-{destination_iata}.")
                break

            self.enforce_rate_limit()
            try:
                target_date = self.calculate_departure_date(window, base_date=base_date)
                quotes = self.scrape_route(
                    origin_iata=origin_iata,
                    destination_iata=destination_iata,
                    booking_window=window,
                    departure_date=target_date,
                )
                all_quotes.extend(quotes)
                self.record_success()
            except Exception as e:
                self.record_failure(e)

        return all_quotes
