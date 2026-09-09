import json
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List
import pandas as pd
import numpy as np
from sqlalchemy import text

# Ensure project root is in Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import CONFIG_DIR, CPI_BASE_INDEX
from database.db import get_engine

def load_route_weights() -> Dict[str, float]:
    """Loads normalized DGCA passenger traffic volume weights (Wi)."""
    with open(CONFIG_DIR / "routes.json", "r", encoding="utf-8") as f:
        routes = json.load(f)
    
    weights = {r["route_id"]: float(r["weight"]) for r in routes}
    total_weight = sum(weights.values())
    
    # Normalize to ensure exact sum = 1.0
    return {k: v / total_weight for k, v in weights.items()}

def compute_all_indices():
    """Computes daily, weekly, and monthly Laspeyres Price Indices from cleaned quotes."""
    engine = get_engine()
    route_weights = load_route_weights()

    # Load cleaned quotes into pandas DataFrame
    query = """
        SELECT route_id, booking_window, carrier_code, portal_id,
               pure_economic_fare, total_published_fare, quote_date
        FROM cleaned_quotes
        WHERE is_outlier = 0
        ORDER BY quote_date ASC
    """
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    if df.empty:
        print("No cleaned quotes found in database. Run 'python manage.py seed-mock' first.")
        return

    df["quote_date"] = pd.to_datetime(df["quote_date"]).dt.date
    dates = sorted(df["quote_date"].unique())

    # Establish Base Period Price (P_i,0): Average of the earliest 3 days
    base_dates = dates[:min(3, len(dates))]
    base_df = df[df["quote_date"].isin(base_dates)]
    
    base_prices = (
        base_df.groupby("route_id")["pure_economic_fare"]
        .median()
        .to_dict()
    )

    print(f"Base Period established across {len(base_prices)} routes using {len(base_dates)} earliest days.")

    # Calculate Route-Level & National Index for each date
    daily_results = []
    route_results = []

    for d in dates:
        date_df = df[df["quote_date"] == d]
        
        # Route-level median prices for this date
        route_medians = (
            date_df.groupby("route_id")["pure_economic_fare"]
            .median()
            .to_dict()
        )
        
        route_totals = (
            date_df.groupby("route_id")["total_published_fare"]
            .median()
            .to_dict()
        )

        route_counts = (
            date_df.groupby("route_id")["pure_economic_fare"]
            .count()
            .to_dict()
        )

        # Compute Laspeyres Index: APIx_t = SUM( (P_i,t / P_i,0) * W_i ) * 100
        weighted_ratios = []
        for route_id, w_i in route_weights.items():
            p_current = route_medians.get(route_id)
            p_base = base_prices.get(route_id)

            if p_current and p_base and p_base > 0:
                price_rel = p_current / p_base
                weighted_ratios.append(price_rel * w_i)

                # Store route-level entry
                route_results.append({
                    "index_date": d,
                    "route_id": route_id,
                    "booking_window": "ALL",
                    "avg_pure_fare": round(float(p_current), 2),
                    "avg_total_fare": round(float(route_totals.get(route_id, p_current)), 2),
                    "quotes_count": int(route_counts.get(route_id, 0))
                })

        if weighted_ratios:
            # Re-normalize if any route was missing today
            current_weight_sum = sum(route_weights[r] for r in route_medians.keys() if r in route_weights)
            apix_t = (sum(weighted_ratios) / current_weight_sum) * CPI_BASE_INDEX
            
            daily_results.append({
                "index_date": d,
                "frequency": "DAILY",
                "apix_value": round(float(apix_t), 2),
                "base_value": CPI_BASE_INDEX,
                "total_quotes_aggregated": len(date_df)
            })

    # Calculate MoM / Rolling Inflation Rate
    for i, res in enumerate(daily_results):
        if i >= 7:  # 7-day comparison
            prev_val = daily_results[i - 7]["apix_value"]
            res["inflation_rate_mom"] = round(((res["apix_value"] - prev_val) / prev_val) * 100, 2)
        else:
            res["inflation_rate_mom"] = round(((res["apix_value"] - CPI_BASE_INDEX) / CPI_BASE_INDEX) * 100, 2)

    # Insert into database
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM daily_index"))
        conn.execute(text("DELETE FROM route_index"))

        for r in daily_results:
            conn.execute(
                text("""
                    INSERT INTO daily_index (index_date, frequency, apix_value, base_value, inflation_rate_mom, total_quotes_aggregated)
                    VALUES (:index_date, :frequency, :apix_value, :base_value, :inflation_rate_mom, :total_quotes_aggregated)
                """),
                r
            )

        for ri in route_results:
            conn.execute(
                text("""
                    INSERT INTO route_index (index_date, route_id, booking_window, avg_pure_fare, avg_total_fare, quotes_count)
                    VALUES (:index_date, :route_id, :booking_window, :avg_pure_fare, :avg_total_fare, :quotes_count)
                """),
                ri
            )

    latest = daily_results[-1]
    print(f"Successfully computed {len(daily_results)} daily APIx index records.")
    print(f"  Latest Date: {latest['index_date']} | APIx: {latest['apix_value']} | 7-Day Change: {latest['inflation_rate_mom']:+.2f}%")

if __name__ == "__main__":
    compute_all_indices()
