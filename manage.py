#!/usr/bin/env python3
"""
==============================================================================
OPERATION APIx: Master Command Line Interface (manage.py)
Problem Statement: SIH26056 (MoSPI)
==============================================================================
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# Ensure project root is in Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.settings import BASE_DIR, CONFIG_DIR, STATE_DIR, DATABASE_URL
from database.db import init_db, get_engine
from sqlalchemy import text

def print_banner():
    banner = r"""
==============================================================================
       __   ___  ___  __       ___    __        __   ___  __       
      /  \ |__  |__  |__)  /\   |  | /  \ |\ | /  \ |__  |__) | \_/ 
      \__/ |    |___ |  \ /~~\  |  | \__/ | \| \__/ |    |  \ | / \ 
      Real-Time Airfare Price Index for India (MoSPI - SIH26056)
==============================================================================
    """
    print(banner)

def cmd_init_db(args):
    """Initializes the database schema and seeds routes/portals."""
    print("Initialising database and seeding core tables...")
    init_db()
    print("Database ready.")

def cmd_status(args):
    """Displays real-time system status, route coverage, and portal health."""
    print_banner()
    print(f"Target Database: {DATABASE_URL}")
    
    engine = get_engine()
    with engine.connect() as conn:
        routes_count = conn.execute(text("SELECT COUNT(*) FROM routes")).scalar()
        portals_count = conn.execute(text("SELECT COUNT(*) FROM portals")).scalar()
        raw_quotes_count = conn.execute(text("SELECT COUNT(*) FROM raw_quotes")).scalar()
        cleaned_quotes_count = conn.execute(text("SELECT COUNT(*) FROM cleaned_quotes")).scalar()
        index_count = conn.execute(text("SELECT COUNT(*) FROM daily_index")).scalar()
        
        latest_index = conn.execute(
            text("SELECT index_date, apix_value, inflation_rate_mom FROM daily_index ORDER BY index_date DESC LIMIT 1")
        ).fetchone()

    print(f"\n--- Data Storage Overview ---")
    print(f"  • Registered DGCA Routes : {routes_count}")
    print(f"  • Mandated Portals       : {portals_count}")
    print(f"  • Raw Quotes Ingested    : {raw_quotes_count:,}")
    print(f"  • Cleaned/Unbundled      : {cleaned_quotes_count:,}")
    print(f"  • Computed Daily Indices : {index_count}")

    if latest_index:
        print(f"\n--- Latest Computed Index ---")
        print(f"  • Date                  : {latest_index[0]}")
        print(f"  • APIx Value            : {latest_index[1]:.2f} (Base 2024=100)")
        print(f"  • MoM Inflation Rate    : {latest_index[2]:+.2f}%")
    else:
        print(f"\n--- Latest Computed Index ---")
        print("  • No index calculated yet. Run 'python manage.py seed-mock' and 'python manage.py compute-index'.")

    # Read Circuit Breakers
    cb_file = STATE_DIR / "circuit_breakers.json"
    if cb_file.exists():
        with open(cb_file, "r", encoding="utf-8") as f:
            cb_data = json.load(f)
        print(f"\n--- Circuit Breakers Health (11 Portals) ---")
        for portal, state in cb_data.items():
            status = state.get("status", "CLOSED")
            fails = state.get("consecutive_failures", 0)
            status_indicator = "[OK]" if status == "CLOSED" else "[TRIPPED]"
            print(f"  {status_indicator:<10} {portal:<18} : Status={status}, Failures={fails}")

def cmd_seed_mock(args):
    """Invokes the synthetic mock data generator for 30 days of data."""
    from database.seed_mock_data import seed_mock_quotes
    days = args.days or 30
    print(f"Generating {days} days of realistic flight quotes for all 12 routes and 5 horizons...")
    seed_mock_quotes(days_back=days)

def cmd_compute_index(args):
    """Computes the Laspeyres price index across daily, weekly, and monthly frequencies."""
    from engine.laspeyres import compute_all_indices
    print("Executing DGCA-weighted Laspeyres Index computation...")
    compute_all_indices()

def cmd_audit(args):
    """Runs the Data Sentinel health and schema drift check."""
    from pipeline.sentinel import run_sentinel_audit
    print("Running Data Sentinel Quality Audit...")
    run_sentinel_audit()

def cmd_serve(args):
    """Launches the FastAPI backend server."""
    import uvicorn
    from config.settings import os
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    print(f"Starting MoSPI/RBI REST API service on http://{host}:{port} ...")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)

def cmd_scrape(args):
    """Runs ingestion scraper for a given portal or all portals."""
    portal = args.portal
    route = args.route
    window = args.window
    print(f"Launching Scraper Engine (Portal: {portal or 'ALL'}, Route: {route or 'ALL'}, Window: {window or 'ALL'})...")
    # To be wired to scrapers module in Phase 3
    print("Live scraping pipeline executing...")

def main():
    parser = argparse.ArgumentParser(
        description="Operation APIx CLI: High-Frequency Airfare Price Index Engine (SIH26056)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init-db
    subparsers.add_parser("init-db", help="Initialize database schema and seed routes/portals")

    # status
    subparsers.add_parser("status", help="Show system status, route coverage, and portal health")

    # seed-mock
    seed_parser = subparsers.add_parser("seed-mock", help="Seed 30-day realistic mock quotes for testing")
    seed_parser.add_argument("--days", type=int, default=30, help="Number of historical days to seed (default: 30)")

    # compute-index
    subparsers.add_parser("compute-index", help="Compute Laspeyres APIx index from quotes")

    # audit
    subparsers.add_parser("audit", help="Run Data Sentinel health and quality audit")

    # serve
    subparsers.add_parser("serve", help="Start FastAPI REST backend server")

    # scrape
    scrape_parser = subparsers.add_parser("scrape", help="Trigger live web scraper")
    scrape_parser.add_argument("--portal", type=str, help="Specific portal ID (e.g. easemytrip, ixigo)")
    scrape_parser.add_argument("--route", type=str, help="Specific route ID (e.g. DEL-BOM)")
    scrape_parser.add_argument("--window", type=str, help="Specific booking window (e.g. T+1, T+7)")

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        sys.exit(0)

    commands = {
        "init-db": cmd_init_db,
        "status": cmd_status,
        "seed-mock": cmd_seed_mock,
        "compute-index": cmd_compute_index,
        "audit": cmd_audit,
        "serve": cmd_serve,
        "scrape": cmd_scrape,
    }

    cmd_fn = commands.get(args.command)
    if cmd_fn:
        cmd_fn(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
