import requests
import json

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/",
})

# Get announcements for BSE
r = session.get("https://www.nseindia.com/api/corporate-announcements?index=equities&symbol=BSE", timeout=15)
data = r.json()

print(f"Total announcements for BSE: {len(data)}")
for i, item in enumerate(data[:10]):
    print(f"--- Item {i} ---")
    print("desc:", item.get("desc"))
    print("attchmntText:", item.get("attchmntText")[:100] if item.get("attchmntText") else None)
    print("attchmntFile:", item.get("attchmntFile"))
    print("dt:", item.get("dt"))
    print("hasXbrl:", item.get("hasXbrl"))

# Look for financial results, investor presentation, transcript
categories = {}
for item in data:
    desc = item.get("desc", "").lower()
    att = item.get("attchmntText", "").lower()
    text = desc + " " + att
    if "result" in text or "financial" in text:
        categories.setdefault("results", []).append(item)
    if "presentation" in text or "investor" in text:
        categories.setdefault("presentation", []).append(item)
    if "transcript" in text or "concall" in text or "call" in text:
        categories.setdefault("transcript", []).append(item)

print("\nCategory counts for BSE:")
for k, v in categories.items():
    print(f"  {k}: {len(v)} matches")
    print(f"    sample 0: dt={v[0].get('dt')}, desc={v[0].get('desc')}, file={v[0].get('attchmntFile')}")

# Check shareholding endpoint
r_sh = session.get("https://www.nseindia.com/api/corporate-share-holdings-master?index=equities&symbol=BSE", timeout=15)
sh_data = r_sh.json()
print(f"\nShareholding items for BSE: {len(sh_data)}")
if sh_data:
    print("Sample shareholding item:", json.dumps(sh_data[0], indent=2))
