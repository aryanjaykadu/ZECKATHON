import requests
import json
import re

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/",
})

symbols = ["BSE", "CDSL", "CAMS", "KFINTECH"]

for sym in symbols:
    url = f"https://www.nseindia.com/api/corporate-announcements?index=equities&symbol={sym}"
    r = session.get(url, timeout=20)
    data = r.json()
    print(f"\n=================== {sym} ({len(data)} total announcements) ===================")
    
    # Filter for financial results
    # Keywords: "Financial Result", "Financial Results", "Outcome of Board Meeting", "Audited Financial Results", "Unaudited Financial Results"
    results = []
    for item in data:
        desc = item.get("desc", "")
        att = item.get("attchmntText", "")
        text = (desc + " " + att).lower()
        
        # Check if it relates to financial results
        if ("financial result" in text or "financial results" in text or "outcome of board meeting" in text) and item.get("attchmntFile"):
            # Exclude trading window, schedule of board meeting (unless outcome), notice of board meeting
            if "trading window" in text or "notice of board meeting" in text or "prior intimation" in text:
                continue
            results.append(item)
            
    print(f"Found {len(results)} potential result announcements")
    for item in results[:15]:
        print(f"  DT: {item.get('dt')} | Desc: {item.get('desc')} | Text: {item.get('attchmntText')[:70]} | File: {item.get('attchmntFile')}")
