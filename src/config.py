import os
from datetime import datetime, date
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
MEMO_DIR = PROJECT_ROOT / "memo"

PROVENANCE_FILE = DATA_DIR / "provenance.csv"
DOWNLOAD_LOG_FILE = DATA_DIR / "download_log.csv"
MISSING_FILE = DATA_DIR / "MISSING.md"

# HARD RULE 1: Cutoff Date
# 2026-10-26 (strictly enforced across all models, loaders, prices)
CUTOFF_DATE_STR = "2026-10-26"
CUTOFF_DATE = date(2026, 10, 26)
CUTOFF_DATETIME = datetime(2026, 10, 26, 23, 59, 59)

# Companies Under Coverage
COMPANIES = {
    "bse": {
        "name": "BSE Limited",
        "ticker_nse": "BSE.NS",
        "symbol": "BSE",
        "scrip_code": "542749",
        "isin": "INE118H01025"
    },
    "cdsl": {
        "name": "Central Depository Services (India) Limited",
        "ticker_nse": "CDSL.NS",
        "symbol": "CDSL",
        "scrip_code": "540526",
        "isin": "INE736A01011"
    },
    "cams": {
        "name": "Computer Age Management Services Limited",
        "ticker_nse": "CAMS.NS",
        "symbol": "CAMS",
        "scrip_code": "543232",
        "isin": "INE596I01012"
    },
    "kfin": {
        "name": "KFin Technologies Limited",
        "ticker_nse": "KFINTECH.NS",
        "symbol": "KFINTECH",
        "scrip_code": "543720",
        "isin": "INE138Y01010"
    }
}

# Portfolio / Mandate Sizing
MANDATE_CAPITAL_INR = 500_00_00_000  # Rs 500 Crore (INR 5 Billion)
RANDOM_SEED = 42

def assert_before_cutoff(dt, context=""):
    """Enforce strict cutoff date rule."""
    if isinstance(dt, str):
        # Format can be YYYY-MM-DD
        d = datetime.strptime(dt[:10], "%Y-%m-%d").date()
    elif isinstance(dt, datetime):
        d = dt.date()
    elif isinstance(dt, date):
        d = dt
    else:
        raise ValueError(f"Unsupported date format {dt}")
    
    assert d <= CUTOFF_DATE, f"HARD RULE VIOLATION: Date {d} exceeds CUTOFF_DATE {CUTOFF_DATE}! Context: {context}"
