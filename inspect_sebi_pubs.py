import requests
import re
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})
r = session.get("https://www.sebi.gov.in/reports-and-statistics/publications.html", timeout=15)
soup = BeautifulSoup(r.text, "html.parser")
print("Title:", soup.title.string if soup.title else None)
for a in soup.find_all("a"):
    href = a.get("href")
    text = a.get_text(strip=True)
    if href and ("bulletin" in href.lower() or "handbook" in href.lower() or "bulletin" in text.lower() or "handbook" in text.lower()):
        print(f"Text: {text} | Link: {href}")
        
# Check if there are form selects or apis
for s in soup.find_all("script"):
    src = s.get("src")
    if src:
        print("Script:", src)
