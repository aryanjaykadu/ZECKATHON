import requests
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

urls = [
    "https://www.rbi.org.in/scripts/AnnualPublications.aspx?head=Handbook+of+Statistics+on+Indian+Economy",
    "https://data.rbi.org.in/DBIE/",
    "https://www.rbi.org.in/Scripts/Statistics.aspx"
]

for u in urls:
    try:
        r = requests.get(u, headers=headers, timeout=15)
        print(f"{u} -> Status: {r.status_code}, len={len(r.content)}")
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a"):
            t = a.get_text(strip=True)
            h = a.get("href", "")
            if any(k in t.lower() for k in ["handbook of statistics", "repo rate", "g-sec", "yield"]):
                print(f"  {t} -> {h}")
    except Exception as e:
        print(f"Error {u}: {e}")
