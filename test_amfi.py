import requests
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

urls = [
    "https://www.amfiindia.com/research-information/amfi-monthly",
    "https://www.amfiindia.com/research-information/aum-data",
    "https://www.amfiindia.com/net-inflow-and-aum"
]

for u in urls:
    try:
        r = requests.get(u, headers=headers, timeout=15)
        print(f"{u} -> Status: {r.status_code}, len={len(r.content)}")
        # Look for excel links
        excels = re.findall(r'href=[\'"]([^\'"]+\.xlsx?[^\'"]*)[\'"]', r.text, re.IGNORECASE)
        print("  Excels:", excels[:5])
    except Exception as e:
        print(f"Error {u}: {e}")
