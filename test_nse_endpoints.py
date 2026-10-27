import requests
import json

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/",
})

# Get initial cookies
try:
    r = session.get("https://www.nseindia.com", timeout=15)
    print("NSE session init:", r.status_code)
except Exception as e:
    print("NSE init failed:", e)

# Test financial results endpoint
# Often: https://www.nseindia.com/api/financial-results?index=equities&symbol=BSE
# or corporate announcements: https://www.nseindia.com/api/corporate-announcements?index=equities&symbol=BSE
endpoints = [
    "https://www.nseindia.com/api/financial-results?index=equities&symbol=BSE",
    "https://www.nseindia.com/api/corporates-financial-results?index=equities&symbol=BSE",
    "https://www.nseindia.com/api/corporate-announcements?index=equities&symbol=BSE",
    "https://www.nseindia.com/api/corporate-share-holdings-master?index=equities&symbol=BSE",
    "https://www.nseindia.com/api/annual-reports?index=equities&symbol=BSE"
]

for ep in endpoints:
    try:
        res = session.get(ep, timeout=15)
        print(f"URL: {ep} -> Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                print(f"   List of {len(data)} items. First item keys: {list(data[0].keys()) if data else []}")
            elif isinstance(data, dict):
                print(f"   Dict keys: {list(data.keys())}")
                for k, v in data.items():
                    if isinstance(v, list):
                        print(f"     {k}: {len(v)} items")
    except Exception as e:
        print(f"Error {ep}: {e}")
