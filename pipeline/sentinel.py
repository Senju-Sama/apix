import json
import sys
from pathlib import Path
from datetime import datetime, date
from sqlalchemy import text

# Ensure project root is in Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import CONFIG_DIR, STATE_DIR
from database.db import get_engine

def run_sentinel_audit():
    """Audits database health, route completeness, and data integrity."""
    engine = get_engine()
    
    with open(CONFIG_DIR / "routes.json", "r", encoding="utf-8") as f:
        target_routes = json.load(f)
    with open(CONFIG_DIR / "windows.json", "r", encoding="utf-8") as f:
        target_windows = json.load(f)

    target_route_ids = {r["route_id"] for r in target_routes}
    target_window_ids = {w["window_id"] for w in target_windows}

    print("\n==============================================================================")
    print("                    DATA SENTINEL: SYSTEM QUALITY AUDIT                       ")
    print("==============================================================================")

    errors = []
    warnings = []

    with engine.connect() as conn:
        # 1. Check Route Coverage
        res_routes = conn.execute(
            text("SELECT DISTINCT route_id FROM cleaned_quotes")
        ).fetchall()
        covered_routes = {r[0] for r in res_routes}
        missing_routes = target_route_ids - covered_routes

        if missing_routes:
            errors.append(f"Missing quotes for {len(missing_routes)} routes: {missing_routes}")
        else:
            print(f"  [PASS] Route Coverage     : 12/12 routes represented ({len(covered_routes)} active).")

        # 2. Check Window Coverage
        res_windows = conn.execute(
            text("SELECT DISTINCT booking_window FROM cleaned_quotes")
        ).fetchall()
        covered_windows = {w[0] for w in res_windows}
        missing_windows = target_window_ids - covered_windows

        if missing_windows:
            errors.append(f"Missing quotes for {len(missing_windows)} booking windows: {missing_windows}")
        else:
            print(f"  [PASS] Window Completeness: 5/5 horizons represented ({', '.join(sorted(covered_windows))}).")

        # 3. Check Fare Value Sanity
        res_negative_fares = conn.execute(
            text("SELECT COUNT(*) FROM raw_quotes WHERE base_fare <= 0 OR total_fare <= 0")
        ).scalar()
        if res_negative_fares > 0:
            errors.append(f"Found {res_negative_fares} raw quotes with zero or negative fares.")
        else:
            print("  [PASS] Fare Value Sanity  : Zero negative or zero-base price anomalies.")

        # 4. Check Fare Coherence (total_fare >= base_fare)
        res_incoherent_fares = conn.execute(
            text("SELECT COUNT(*) FROM raw_quotes WHERE total_fare < base_fare")
        ).scalar()
        if res_incoherent_fares > 0:
            errors.append(f"Found {res_incoherent_fares} quotes where total_fare < base_fare.")
        else:
            print("  [PASS] Fare Coherence     : All total fares >= base fares.")

        # 5. Check Index Coverage
        index_count = conn.execute(text("SELECT COUNT(*) FROM daily_index")).scalar()
        if index_count == 0:
            warnings.append("No daily index calculated yet. Run 'python manage.py compute-index'.")
        else:
            print(f"  [PASS] Index Generation   : {index_count} daily APIx time-series points generated.")

    # Update state/pipeline_state.json
    state_file = STATE_DIR / "pipeline_state.json"
    with open(state_file, "r", encoding="utf-8") as f:
        pipeline_state = json.load(f)

    health_status = "HEALTHY" if not errors else "DEGRADED"
    pipeline_state["system_status"] = health_status
    pipeline_state["last_audit_timestamp"] = datetime.utcnow().isoformat()

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(pipeline_state, f, indent=2)

    print("------------------------------------------------------------------------------")
    if errors:
        print(f"  [ALERT] System Status: {health_status} with {len(errors)} error(s):")
        for err in errors:
            print(f"    - {err}")
        return False
    else:
        print("  [SUCCESS] All Sentinel Quality Gates PASSED (Health Score: 100%).")
        print("==============================================================================\n")
        return True

if __name__ == "__main__":
    run_sentinel_audit()
