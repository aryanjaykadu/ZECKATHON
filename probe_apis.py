# Attempt to download annual reports for BSE Ltd, CAMS, KFin via BSE India
# corporate filings API and direct URL patterns.
import sys, os, json, time
sys.path.insert(0, os.getcwd())
from download_utils import download_file, log_missing
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.bseindia.com/",
}

# BSE scrip codes
COMPANIES = {
    "bse": {"scrip": "542749", "name": "BSE Limited", "nse": "BSE"},
    "cams": {"scrip": "543232", "name": "CAMS", "nse": "CAMS"},
    "kfin": {"scrip": "543720", "name": "KFin Technologies", "nse": "KFINTECH"},
}

# Try BSE API for annual reports
# Endpoint: https://api.bseindia.com/BseIndiaAPI/api/AnnualReport/w?scripcode=XXXXX
for key, info in COMPANIES.items():
    scrip = info["scrip"]
    name = info["name"]
    print(f"\n{'='*60}")
    print(f"Trying BSE API for {name} (scrip={scrip})")
    print(f"{'='*60}")
    
    api_url = f"https://api.bseindia.com/BseIndiaAPI/api/AnnualReport/w?scripcode={scrip}"
    try:
        r = requests.get(api_url, headers=HEADERS, timeout=30)
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"  Found {len(data)} entries")
                for item in data[:10]:
                    print(f"    {json.dumps(item, indent=2)[:200]}")
            elif isinstance(data, dict):
                print(f"  Response: {json.dumps(data, indent=2)[:500]}")
            else:
                print(f"  Response type: {type(data)}, content: {str(data)[:500]}")
        else:
            print(f"  Response: {r.text[:500]}")
    except Exception as e:
        print(f"  Error: {e}")
    time.sleep(2)

# Also try NSE API for corporate filings
print(f"\n{'='*60}")
print("Trying NSE API for corporate filings")
print(f"{'='*60}")

nse_session = requests.Session()
nse_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
})

# First hit main page to get cookies
try:
    nse_session.get("https://www.nseindia.com", timeout=15)
    time.sleep(2)
except:
    pass

for key, info in COMPANIES.items():
    symbol = info["nse"]
    name = info["name"]
    print(f"\n  NSE: {name} ({symbol})")
    
    # Try annual reports endpoint
    ar_url = f"https://www.nseindia.com/api/annual-reports?index=equities&symbol={symbol}"
    try:
        r = nse_session.get(ar_url, timeout=30)
        print(f"    Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"    Response: {json.dumps(data, indent=2)[:1000]}")
        else:
            print(f"    Headers: {dict(r.headers)}")
            print(f"    Body: {r.text[:300]}")
    except Exception as e:
        print(f"    Error: {e}")
    time.sleep(3)
