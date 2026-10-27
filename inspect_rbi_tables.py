import requests
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Check Table 178: Government Dated Securities Yields
url_178 = "https://www.rbi.org.in/scripts/PublicationsView.aspx?id=24003"
r = requests.get(url_178, headers=headers, timeout=20)
print(f"Table 178 status: {r.status_code}, len={len(r.content)}")
soup = BeautifulSoup(r.text, "html.parser")
print("Table 178 title:", soup.title.string if soup.title else None)
excels = [a.get("href") for a in soup.find_all("a") if a.get("href") and any(ext in a.get("href").lower() for ext in [".xls", ".xlsx", ".csv"])]
print("Table 178 Excel links:", excels)

# Find all tables in Handbook related to Interest rates or Policy rates
url_hb = "https://www.rbi.org.in/scripts/AnnualPublications.aspx?head=Handbook+of+Statistics+on+Indian+Economy"
r_hb = requests.get(url_hb, headers=headers, timeout=20)
soup_hb = BeautifulSoup(r_hb.text, "html.parser")

found = []
for a in soup_hb.find_all("a"):
    t = a.get_text(strip=True)
    h = a.get("href", "")
    if any(k in t.lower() for k in ["rate", "yield", "call money", "policy", "treasury"]):
        found.append((t, h))

print(f"\nFound {len(found)} candidate tables in Handbook:")
for t, h in found[:15]:
    try:
        print(f"  {t} -> {h}")
    except:
        pass
