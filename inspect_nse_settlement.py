import requests
import re
import json

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.nseindia.com/",
})

# First get homepage to get cookies
session.get("https://www.nseindia.com", timeout=15)

url = "https://www.nseindia.com/all-reports/historical-reports-equity-market-monthly-settlement-statistics"
r = session.get(url, timeout=15)
print("Page status:", r.status_code)
# Look for api endpoints or csv/xlsx links
links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', r.text)
csv_links = [l for l in links if any(ext in l.lower() for ext in ['.csv', '.xlsx', '.xls', '.zip', 'api'])]
print("Found links:", csv_links[:10])

# Check scripts
scripts = re.findall(r'src=[\'"]([^\'"]+\.js)[\'"]', r.text)
print("Scripts:", scripts[:5])
