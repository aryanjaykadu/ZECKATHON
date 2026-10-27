import os
import sys
import shutil

sys.path.insert(0, os.getcwd())
from download_utils import download_file

macro_dir = os.path.join("data", "raw", "macro")
os.makedirs(macro_dir, exist_ok=True)

print("="*60)
print("Downloading Official Macro Data from RBI Handbook of Statistics")
print("="*60)

# 1. RBI Repo Rate and Monetary Policy Rates
repo_url = "https://rbidocs.rbi.org.in/rdocs/Publications/DOCs/40T_HBIE31072026FF3E894445944DA8A3C011F1653F999A.XLSX"
repo_dest = os.path.join(macro_dir, "RBI_Table_40_Policy_Repo_Rates_and_Reserve_Requirements.xlsx")
ok1 = download_file(
    repo_url, repo_dest, "RBI", "macro_repo_rate",
    page_title="RBI Handbook of Statistics - Table 40: Major Monetary Policy Rates and Reserve Requirements",
    pub_date="2026-07-31",
    notes="Official historical series of Bank Rate, Repo Rate, Reverse Repo, SDF, MSF, CRR, and SLR",
    referer="https://www.rbi.org.in"
)

# 2. 10-Year Government Security Yield
gsec_url = "https://rbidocs.rbi.org.in/rdocs/Publications/DOCs/178T_HBIE310720260B5138FE9BE24FC0939F05E5EE409982.XLSX"
gsec_dest = os.path.join(macro_dir, "RBI_Table_178_Government_Dated_Securities_Yields_10Y.xlsx")
ok2 = download_file(
    gsec_url, gsec_dest, "RBI", "macro_gsec_10yr",
    page_title="RBI Handbook of Statistics - Table 178: Month-end Yield of SGL Transactions in Government Dated Securities",
    pub_date="2026-07-31",
    notes="Official historical series of Government Dated Securities Yields across maturities including 10-year G-sec benchmark",
    referer="https://www.rbi.org.in"
)

# 3. Nifty 50 History
prices_nifty = os.path.join("data", "raw", "prices", "NSEI_daily_ohlcv.csv")
macro_nifty = os.path.join(macro_dir, "NIFTY50_daily_ohlcv.csv")
if os.path.exists(prices_nifty) and not os.path.exists(macro_nifty):
    shutil.copy(prices_nifty, macro_nifty)
    print(f"  Copied Nifty 50 daily OHLCV to macro directory: {macro_nifty}")

print("\nMacro download complete.")
