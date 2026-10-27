import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

url = "https://www.rbi.org.in/scripts/AnnualPublications.aspx?head=Handbook+of+Statistics+on+Indian+Economy"
r = requests.get(url, headers=headers, timeout=20)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.find_all("a"):
    t = a.get_text(strip=True)
    h = a.get("href", "")
    if any(k in t.lower() for k in ["repo", "policy rate", "interest rate", "bank rate", "laf", "call money", "marginal standing", "standing deposit"]):
        print(f"{t} -> https://www.rbi.org.in/scripts/{h}")
