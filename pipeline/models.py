import hashlib
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

class FareBreakdown(BaseModel):
    """Decomposed airfare pricing elements as mandated by MoSPI."""
    base_fare: float = Field(..., description="Pure airline seat price (core CPI economic variable)")
    fuel_surcharge: float = Field(default=0.0, description="Airline fuel surcharge / Carrier charges (YQ/YR)")
    taxes_and_fees: float = Field(default=0.0, description="Statutory fees: GST, UDF, PSF, ASF")
    convenience_fee: float = Field(default=0.0, description="OTA intermediary booking fee")
    total_fare: float = Field(..., description="Final published price paid by consumer")

    @field_validator("base_fare", "total_fare")
    @classmethod
    def validate_positive_fare(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Fare components cannot be negative")
        return round(v, 2)

    @model_validator(mode="after")
    def validate_fare_coherence(self):
        # Total fare must be at least the base fare
        if self.total_fare < self.base_fare:
            raise ValueError(f"Total fare ({self.total_fare}) cannot be less than base fare ({self.base_fare})")
        return self

class RawFlightQuote(BaseModel):
    """Raw ingestion schema emitted by all 11 scraper adapters."""
    scrape_timestamp: datetime = Field(default_factory=datetime.utcnow)
    portal_id: str = Field(..., description="Mandated portal identifier (e.g. easemytrip, indigo)")
    carrier_code: Optional[str] = Field(default=None, description="2-letter IATA carrier code (e.g. 6E, AI)")
    carrier_name: Optional[str] = Field(default=None, description="Airline name")
    flight_number: Optional[str] = Field(default=None, description="Flight number code (e.g. 6E-2045)")
    origin_iata: str = Field(..., min_length=3, max_length=3, description="3-letter IATA origin")
    destination_iata: str = Field(..., min_length=3, max_length=3, description="3-letter IATA destination")
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    booking_window: str = Field(..., description="Horizon: T+1, T+7, T+15, T+30, T+45")
    is_non_stop: bool = Field(default=True)
    fare: FareBreakdown
    seats_available: Optional[int] = Field(default=None)
    is_sold_out: bool = Field(default=False)

    @field_validator("origin_iata", "destination_iata")
    @classmethod
    def uppercase_iata(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("booking_window")
    @classmethod
    def validate_window(cls, v: str) -> str:
        valid_windows = {"T+1", "T+7", "T+15", "T+30", "T+45"}
        clean_v = v.strip().upper()
        if clean_v not in valid_windows:
            raise ValueError(f"Invalid booking window: {v}. Must be one of {valid_windows}")
        return clean_v

    @property
    def dedup_hash(self) -> str:
        """Computes deterministic SHA256 deduplication key."""
        components = [
            self.portal_id,
            self.carrier_code or "UNK",
            self.flight_number or "FLT",
            self.origin_iata,
            self.destination_iata,
            self.departure_time.isoformat() if self.departure_time else "NODEP",
            self.booking_window,
            self.scrape_timestamp.strftime("%Y-%m-%d")
        ]
        raw_key = "|".join(components)
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

class CleanedFlightQuote(BaseModel):
    """Post-unbundled and outlier-inspected quote ready for index aggregation."""
    raw_quote_id: Optional[int] = None
    route_id: str = Field(..., description="City-pair route code, e.g. DEL-BOM")
    booking_window: str
    carrier_code: str
    portal_id: str
    pure_economic_fare: float = Field(..., description="Base Fare + Fuel Surcharge (YQ)")
    total_published_fare: float
    is_outlier: bool = False
    outlier_reason: Optional[str] = None
    quote_date: date

class DailyIndexResult(BaseModel):
    """Computed Laspeyres price index output for a specific date and frequency."""
    index_date: date
    frequency: str = Field(default="DAILY")  # 'DAILY', 'WEEKLY', 'MONTHLY'
    apix_value: float
    base_value: float = 100.0
    inflation_rate_mom: Optional[float] = None
    total_quotes_aggregated: int
