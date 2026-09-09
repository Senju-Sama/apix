import os
import sys
import json
import unittest
from datetime import date, datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline.models import RawFlightQuote
from scrapers.otas.easemytrip_scraper import EaseMyTripScraper

class TestEaseMyTripScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = EaseMyTripScraper()

    def test_url_construction(self):
        target_date = date(2026, 9, 16)
        url = self.scraper._build_search_url("DEL", "BOM", target_date)
        self.assertIn("DEL-Delhi-India", url)
        self.assertIn("BOM-Mumbai-India", url)
        self.assertIn("16/09/2026", url)
        self.assertIn("px=1-0-0", url)

    def test_parse_airbus_payload_from_sample(self):
        # Load intercepted sample
        with open("scratch/emt_intercepted_sample.json", "r", encoding="utf-8") as f:
            sample_data = json.load(f)
        
        if isinstance(sample_data, list):
            airbus_payload = sample_data[1]["body_json"]
        elif isinstance(sample_data, dict) and "body_json" in sample_data:
            airbus_payload = sample_data["body_json"]
        else:
            airbus_payload = sample_data
        
        target_date = date(2026, 9, 16)
        quotes = self.scraper._parse_airbus_payload(
            payload=airbus_payload,
            origin_iata="DEL",
            destination_iata="BOM",
            booking_window="T+7",
            target_date=target_date,
        )

        self.assertGreater(len(quotes), 50, "Should extract at least 50 flight quotes")
        print(f"\n[TEST PASS] Extracted {len(quotes)} flight quotes from intercepted sample.")

        # Test first quote properties
        q = quotes[0]
        self.assertIsInstance(q, RawFlightQuote)
        self.assertEqual(q.origin_iata, "DEL")
        self.assertEqual(q.destination_iata, "BOM")
        self.assertEqual(q.portal_id, "easemytrip")
        self.assertEqual(q.booking_window, "T+7")
        self.assertIsNotNone(q.carrier_code)
        self.assertIsNotNone(q.flight_number)
        self.assertGreater(q.fare.total_fare, 0)
        self.assertGreater(q.fare.base_fare, 0)
        self.assertGreater(len(q.dedup_hash), 20)

        # Check carriers present
        carriers = set(q.carrier_code for q in quotes)
        print(f"[TEST PASS] Carriers extracted: {carriers}")
        self.assertTrue(any(c in carriers for c in ["6E", "AI", "QP", "SG"]))

        # Check non-stop count
        non_stop_count = sum(1 for q in quotes if q.is_non_stop)
        print(f"[TEST PASS] Non-stop quotes: {non_stop_count} out of {len(quotes)}")
        self.assertGreater(non_stop_count, 10)

if __name__ == "__main__":
    unittest.main()
