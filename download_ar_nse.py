# Download annual reports for BSE Ltd, CAMS, KFin, CDSL via NSE Archives API.
# Also tries BSE API for CAMS and KFin as backup.
import sys, os, json, time
sys.path.insert(0, os.getcwd())
from download_utils import download_file, log_missing
import requests

HEADERS_NSE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
}

# NSE symbols
SYMBOLS = {
    "bse": "BSE",
    "cdsl": "CDSL",
    "cams": "CAMS",
    "kfin": "KFINTECH",
}

# We need last 5 fiscal years: FY2025-26, FY2024-25, FY2023-24, FY2022-23, FY2021-22
NEEDED_FY = [("2025","2026"), ("2024","2025"), ("2023","2024"), ("2022","2023"), ("2021","2022")]

# First establish session with NSE
session = requests.Session()
session.headers.update(HEADERS_NSE)
try:
    session.get("https://www.nseindia.com", timeout=15)
    time.sleep(2)
except:
    pass

for company, symbol in SYMBOLS.items():
    if company == "cdsl":
        print(f"\nSkipping CDSL - already downloaded from cdslindia.com directly")
        continue
    
    print(f"\n{'='*60}")
    print(f"Downloading annual reports for {symbol}")
    print(f"{'='*60}")
    
    url = f"https://www.nseindia.com/api/annual-reports?index=equities&symbol={symbol}"
    try:
        r = session.get(url, timeout=30)
        if r.status_code != 200:
            print(f"  NSE API returned {r.status_code}, skipping")
            for fy_from, fy_to in NEEDED_FY:
                log_missing(company.upper(), "annual_report",
                    f"Annual Report FY{fy_from}-{fy_to[-2:]}",
                    "1 - NSE API failed",
                    f"https://www.nseindia.com/companies-listing/corporate-filings-annual-reports")
            continue
        
        data = r.json().get("data", [])
        print(f"  Found {len(data)} entries from NSE API")
        
        # Map by fiscal year
        fy_map = {}
        for item in data:
            fy_key = (item.get("fromYr"), item.get("toYr"))
            if fy_key not in fy_map:
                fy_map[fy_key] = item
        
        for fy_from, fy_to in NEEDED_FY:
            fy_label = f"FY{fy_from}-{fy_to[-2:]}"
            item = fy_map.get((fy_from, fy_to))
            if not item:
                print(f"  {fy_label}: Not found in NSE data")
                log_missing(company.upper(), "annual_report",
                    f"Annual Report {fy_label}",
                    "1 - not in NSE API response",
                    "https://www.nseindia.com/companies-listing/corporate-filings-annual-reports")
                continue
            
            pdf_url = item.get("fileName", "")
            if not pdf_url or not pdf_url.startswith("http"):
                print(f"  {fy_label}: No PDF URL in response")
                log_missing(company.upper(), "annual_report",
                    f"Annual Report {fy_label}",
                    "1 - no PDF URL",
                    "https://www.nseindia.com/companies-listing/corporate-filings-annual-reports")
                continue
            
            dest = os.path.join("data", "raw", company, "annual_reports",
                f"{symbol}_AR_{fy_label}.pdf")
            
            pub_date = item.get("broadcast_dttm", "")
            ok = download_file(
                pdf_url, dest, company.upper(), "annual_report",
                page_title=f"NSE Corporate Filings - {item.get('companyName','')}",
                pub_date=fy_label,
                notes=f"Via NSE API. Published: {pub_date}. Size: {item.get('attFileSize','')}",
                referer="https://www.nseindia.com/companies-listing/corporate-filings-annual-reports"
            )
            if not ok:
                log_missing(company.upper(), "annual_report",
                    f"Annual Report {fy_label}",
                    "1 - download failed",
                    pdf_url)
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(3)

# Now also get BSE Ltd annual reports from NSE API (we need the full data)
print(f"\n{'='*60}")
print("Re-checking BSE Ltd from NSE API with full data")
print(f"{'='*60}")

# Refresh session
try:
    session.get("https://www.nseindia.com", timeout=15)
    time.sleep(2)
except:
    pass

url = "https://www.nseindia.com/api/annual-reports?index=equities&symbol=BSE"
try:
    r = session.get(url, timeout=30)
    if r.status_code == 200:
        data = r.json().get("data", [])
        print(f"  Full response ({len(data)} items):")
        for item in data:
            print(f"    FY{item.get('fromYr')}-{item.get('toYr')}: {item.get('fileName','N/A')}")
except Exception as e:
    print(f"  Error: {e}")

print("\nDone.")
