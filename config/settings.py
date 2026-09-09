import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")

# Project Metadata
PROJECT_NAME = "Operation APIx - Airfare Price Index for India"
PROBLEM_STATEMENT_ID = "SIH26056"
SPONSOR_MINISTRY = "MoSPI (DIID)"

# Database Configuration (SQLite default -> Supabase PostgreSQL ready)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"sqlite:///{BASE_DIR / 'database' / 'apix.db'}"
)

# Directory Paths
CONFIG_DIR = BASE_DIR / "config"
MEMORY_DIR = BASE_DIR / "memory"
STATE_DIR = BASE_DIR / "state"
DATABASE_DIR = BASE_DIR / "database"
CACHE_DIR = DATABASE_DIR / "cache"
BENCHMARKS_DIR = BASE_DIR / "benchmarks"

# Anti-Bot & Network Settings
DEFAULT_USER_AGENT = os.getenv(
    "USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
CIRCUIT_BREAKER_FAIL_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_FAIL_THRESHOLD", "3"))
CIRCUIT_BREAKER_COOLDOWN_SECONDS = int(os.getenv("CIRCUIT_BREAKER_COOLDOWN_SECONDS", "1800"))

# Base Year Calibration for CPI
CPI_BASE_YEAR = 2024
CPI_BASE_INDEX = 100.0
