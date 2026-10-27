import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})

# 1. Monthly SEBI Bulletin
url_bulletin = "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=4&ssid=80&smid=107"
r = session.get(url_bulletin, timeout=15)
print("Bulletin listing status:", r.status_code, len(r.content))
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.find_all("a"):
    href = a.get("href", "")
    text = a.get_text(strip=True)
    if "bulletin" in text.lower() or "table" in text.lower() or "2026" in text or "2025" in text:
        print(f"Bulletin: {text} -> {href}")

# 2. Handbook of Statistics
url_hb = "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=4&ssid=80&smid=105"
r_hb = session.get(url_hb, timeout=15)
print("\nHandbook listing status:", r_hb.status_code, len(r_hb.content))
soup_hb = BeautifulSoup(r_hb.text, "html.parser")
for a in soup_hb.find_all("a"):
    href = a.get("href", "")
    text = a.get_text(strip=True)
    if "handbook" in text.lower() or "statistics" in text.lower() or "2026" in text or "2025" in text or "2024" in text:
        print(f"Handbook: {text} -> {href}")
