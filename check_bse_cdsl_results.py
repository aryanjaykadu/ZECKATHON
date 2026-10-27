import requests
import json
from datetime import datetime

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/",
})

for sym in ["BSE", "CDSL"]:
    r = session.get(f"https://www.nseindia.com/api/corporate-announcements?index=equities&symbol={sym}", timeout=20)
    print(f"\n=================== {sym} Financial Results ===================")
    items = r.json()
    count = 0
    for item in items:
        desc = item.get("desc", "")
        att = item.get("attchmntText", "")
        text = (desc + " " + att).lower()
        if "financial result" in text or "outcome of board meeting" in text:
            if any(w in text for w in ["trading window", "notice", "prior intimation", "schedule of meet"]):
                continue
            dt_str = item.get("dt", "")
            file_url = item.get("attchmntFile", "")
            if file_url:
                print(f"Date: {dt_str[:8]} | Desc: {desc} | File: {file_url}")
                print(f"   Text: {att[:120]}")
                count += 1
                if count >= 12:
                    break
