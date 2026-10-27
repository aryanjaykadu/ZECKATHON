import requests
import json
import os
import sys

sys.path.insert(0, os.getcwd())
from download_utils import download_file, log_missing

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})

# Try the new URL: 84781.html
test_urls = [
    "https://www.sebi.gov.in/legal/circulars/jul-2024/charges-levied-by-market-infrastructure-institutions-true-to-label_84781.html",
    "https://www.sebi.gov.in/sebi_data/attachdocs/jul-2024/1719833502931.pdf",
    "https://www.sebi.gov.in/legal/circulars/oct-2024/measures-to-strengthen-equity-index-derivatives-framework-for-increased-investor-protection-and-market-stability_87164.html",
    "https://www.sebi.gov.in/legal/circulars/oct-2024/measures-to-strengthen-equity-index-derivatives-framework-for-increased-investor-protection-and-market-stability_87081.html"
]

for url in test_urls:
    try:
        r = session.get(url, timeout=15)
        print(f"{url} -> {r.status_code} ({len(r.content)} bytes)")
    except Exception as e:
        print(f"{url} -> Error: {e}")
