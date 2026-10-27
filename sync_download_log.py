import os
import csv
import hashlib
from datetime import datetime

LOG_FILE = os.path.join("data", "download_log.csv")
TODAY = datetime.now().strftime("%Y-%m-%d")

# Read existing log entries
existing_files = set()
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if row:
                existing_files.add(row[0])

print(f"Existing rows in log: {len(existing_files)}")

# Map folder to entity & data_type
def get_entity_and_type(root, fname):
    parts = root.replace("\\", "/").split("/")
    if "prices" in parts:
        return "Market", "daily_ohlcv", "Yahoo Finance (yfinance)", "https://finance.yahoo.com"
    elif "macro" in parts:
        if "NIFTY" in fname:
            return "Macro/NSE", "macro_nifty50", "NSE / Yahoo Finance", "https://finance.yahoo.com"
        else:
            return "RBI", "macro_interest_rates", "RBI Handbook of Statistics", "https://www.rbi.org.in"
    elif "regulation" in parts:
        return "SEBI/Exchanges", "regulation_circular", "SEBI / NSE / BSE Regulatory Archives", "https://nsearchives.nseindia.com"
    elif "industry" in parts:
        if "amfi" in parts:
            return "AMFI", "industry_amfi_monthly", "AMFI India Research", "https://www.amfiindia.com/research-information/amfi-monthly"
        elif "derivatives_turnover" in parts:
            return "SEBI/Exchanges", "industry_derivatives_turnover", "SEBI Monthly Bulletin", "https://www.sebi.gov.in"
        elif "demat" in parts:
            return "SEBI/Depositories", "industry_demat_accounts", "SEBI Monthly Bulletin", "https://www.sebi.gov.in"
    else:
        # Company filings
        comp = parts[2].upper()
        dtype = parts[3]
        return comp, dtype, f"{comp} Corporate Filings", "https://www.nseindia.com"

# Check all files in data/raw
added = 0
with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for root, dirs, files in os.walk("data/raw"):
        for fname in files:
            if fname not in existing_files:
                fpath = os.path.join(root, fname)
                sz = os.path.getsize(fpath)
                sha = hashlib.sha256(open(fpath, "rb").read()).hexdigest()
                entity, dtype, title, url = get_entity_and_type(root, fname)
                writer.writerow([
                    fname, entity, dtype, url, title, "historical", TODAY, sha, f"Size={sz:,}B"
                ])
                existing_files.add(fname)
                added += 1

print(f"Added {added} missing files to download_log.csv. Total rows now: {len(existing_files)}")
