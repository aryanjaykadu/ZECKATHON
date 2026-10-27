import requests
import re
from bs4 import BeautifulSoup
import os
import sys

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

r = requests.get("https://www.amfiindia.com/research-information/amfi-monthly", headers=headers, timeout=20)
links = re.findall(r'href=[\'"]([^\'"]+\.xls[^\'"]*)[\'"]', r.text, re.IGNORECASE)
print(f"Total excel links found: {len(links)}")
for l in links[:20]:
    print(" ", l)
