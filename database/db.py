import json
import sqlite3
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import sys

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import DATABASE_URL, BASE_DIR, CONFIG_DIR, DATABASE_DIR

_engine: Engine = None

def get_engine() -> Engine:
    """Returns the SQLAlchemy engine configured for SQLite or Supabase PostgreSQL."""
    global _engine
    if _engine is None:
        # SQLite specific configuration
        if DATABASE_URL.startswith("sqlite"):
            # Ensure database directory exists
            DATABASE_DIR.mkdir(parents=True, exist_ok=True)
            _engine = create_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False},
                echo=False
            )
        else:
            # PostgreSQL / Supabase pool configuration
            _engine = create_engine(
                DATABASE_URL,
                pool_size=10,
                max_overflow=20,
                pool_recycle=300,
                echo=False
            )
    return _engine

def init_db():
    """Initializes the database schema and populates base routes and portals."""
    engine = get_engine()
    schema_file = DATABASE_DIR / "schema.sql"
    
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    # If SQLite, execute via raw connection to handle multiple statements cleanly
    if DATABASE_URL.startswith("sqlite"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
    else:
        with engine.begin() as conn:
            for statement in schema_sql.split(";"):
                stmt = statement.strip()
                if stmt:
                    conn.execute(text(stmt))

    # Seed Routes from config/routes.json if not already present
    seed_routes_and_portals()
    print("Database schema initialized successfully.")

def seed_routes_and_portals():
    """Seeds the 12 DGCA routes and 11 portals into the database."""
    engine = get_engine()
    routes_file = CONFIG_DIR / "routes.json"
    sources_file = CONFIG_DIR / "sources.json"

    with open(routes_file, "r", encoding="utf-8") as f:
        routes_data = json.load(f)

    with open(sources_file, "r", encoding="utf-8") as f:
        sources_data = json.load(f)

    with engine.begin() as conn:
        # Check existing routes count
        res = conn.execute(text("SELECT COUNT(*) FROM routes")).scalar()
        if res == 0:
            for r in routes_data:
                conn.execute(
                    text("""
                        INSERT INTO routes (route_id, origin_iata, origin_city, destination_iata, destination_city, classification, weight, ps_mandated)
                        VALUES (:route_id, :origin_iata, :origin_city, :destination_iata, :destination_city, :classification, :weight, :ps_mandated)
                    """),
                    r
                )
            print(f"Seeded {len(routes_data)} representative DGCA routes.")

        # Check existing portals count
        res_portals = conn.execute(text("SELECT COUNT(*) FROM portals")).scalar()
        if res_portals == 0:
            for s in sources_data:
                conn.execute(
                    text("""
                        INSERT INTO portals (id, name, type, carrier_code, domain, method, is_active)
                        VALUES (:id, :name, :type, :carrier_code, :domain, :method, :is_active)
                    """),
                    {
                        "id": s["id"],
                        "name": s["name"],
                        "type": s["type"],
                        "carrier_code": s.get("carrier_code"),
                        "domain": s["domain"],
                        "method": s["method"],
                        "is_active": s.get("is_active", True)
                    }
                )
            print(f"Seeded {len(sources_data)} mandated portals.")

if __name__ == "__main__":
    init_db()
