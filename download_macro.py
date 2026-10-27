# Download macro data: RBI repo rate history, 10-yr G-sec yield, Nifty 50 history
import sys, os, json, time, csv, hashlib
sys.path.insert(0, os.getcwd())
from download_utils import download_file, log_missing
import requests
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = os.path.join("data", "download_log.csv")
MACRO_DIR = os.path.join("data", "raw", "macro")

# ============================================================
# 1. RBI Repo Rate History from DBIE
# ============================================================
print("=" * 60)
print("RBI Repo Rate History")
print("=" * 60)

# Try DBIE API for repo rate
# The RBI publishes key rates at: https://www.rbi.org.in/scripts/BS_NSDPDisplay.aspx?param=4
rbi_url = "https://www.rbi.org.in/scripts/BS_NSDPDisplay.aspx?param=4"
dest = os.path.join(MACRO_DIR, "rbi_policy_rates_page.html")
ok = download_file(rbi_url, dest, "RBI", "macro_repo_rate",
    page_title="RBI - Current Rates", pub_date="current",
    notes="HTML page with current policy rates")

# Also try the Excel from DBIE
# https://dbie.rbi.org.in/DBIE/dbie.rbi?site=statistics#!4_2
# Direct URL for repo rate history Excel
dbie_urls = [
    ("https://rbidocs.rbi.org.in/rdocs/Publications/DOCs/T_02122024CB8E71B6DD4F49D5BB8B1A8EC4E66C9F.XLSX",
     "rbi_repo_rate_history.xlsx", "RBI Handbook of Statistics - Repo Rate"),
    ("https://rbidocs.rbi.org.in/rdocs/content/docs/CRRSLRREPOREVERSE.XLS",
     "rbi_crr_slr_repo.xls", "RBI CRR SLR Repo Rate History"),
]

for url, fname, title in dbie_urls:
    dest = os.path.join(MACRO_DIR, fname)
    ok = download_file(url, dest, "RBI", "macro_repo_rate",
        page_title=title, pub_date="historical",
        notes="Historical policy rates")
    if ok:
        break

# Try a known DBIE excel
rbi_excel_url = "https://rbidocs.rbi.org.in/rdocs/content/docs/CRRSLRREPOREVERSE.XLS"
dest_xls = os.path.join(MACRO_DIR, "rbi_policy_rates.xls")
download_file(rbi_excel_url, dest_xls, "RBI", "macro_repo_rate",
    page_title="RBI Policy Rates XLS", pub_date="historical",
    notes="CRR/SLR/Repo/Reverse Repo historical data")

if not os.path.exists(dest_xls) or os.path.getsize(dest_xls) < 1000:
    log_missing("RBI", "macro_repo_rate", "Repo rate history spreadsheet",
        "3 - tried multiple DBIE URLs",
        "https://dbie.rbi.org.in - search for 'Policy Repo Rate'")

# ============================================================
# 2. 10-Year G-Sec Yield
# ============================================================
print("\n" + "=" * 60)
print("10-Year G-Sec Yield")
print("=" * 60)

# Try to get from RBI DBIE or FBIL
gsec_urls = [
    "https://rbidocs.rbi.org.in/rdocs/content/docs/GSEC10YEAR.XLS",
    "https://www.fbil.org.in/api/gsec-benchmarks?tenor=10Y",
]

for url in gsec_urls:
    ext = ".xls" if url.endswith(".XLS") else ".json"
    dest = os.path.join(MACRO_DIR, f"gsec_10yr_yield{ext}")
    ok = download_file(url, dest, "RBI/FBIL", "macro_gsec_10yr",
        page_title="10-Year G-Sec Yield", pub_date="historical",
        notes="10-year government security benchmark yield")
    if ok:
        break

# ============================================================
# 3. Nifty 50 History - already covered via yfinance (^NSEI)
# ============================================================
print("\n" + "=" * 60)
print("Nifty 50 - Already downloaded via yfinance as NSEI_daily_ohlcv.csv")
print("=" * 60)

# Copy/symlink is not needed - it's already in data/raw/prices/
nifty_path = os.path.join("data", "raw", "prices", "NSEI_daily_ohlcv.csv")
if os.path.exists(nifty_path):
    print(f"  Already exists: {nifty_path} ({os.path.getsize(nifty_path):,} bytes)")
else:
    log_missing("NSE", "macro_nifty50", "Nifty 50 daily OHLCV",
        "Should have been downloaded in price step",
        "Run download_prices.py again")

print("\nMacro data download complete.")
