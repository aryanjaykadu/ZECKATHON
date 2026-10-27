import requests
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

url = "https://www.cdslindia.com/publications/bostats.aspx"
r = requests.get(url, headers=headers, timeout=15)
print("CDSL BO stats status:", r.status_code, len(r.content))
if r.status_code == 200:
    links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', r.text)
    excel_or_pdf = [l for l in links if any(ext in l.lower() for ext in ['.xls', '.xlsx', '.csv', '.pdf'])]
    print("Files:", excel_or_pdf[:10])
    
# Also check NSDL publications
url_nsdl = "https://nsdl.co.in/publications/nest.php"
try:
    r_nsdl = requests.get(url_nsdl, headers=headers, timeout=15)
    print("NSDL nest status:", r_nsdl.status_code, len(r_nsdl.content))
    if r_nsdl.status_code == 200:
        links_nsdl = re.findall(r'href=[\'"]([^\'"]+)[\'"]', r_nsdl.text)
        nsdl_files = [l for l in links_nsdl if any(ext in l.lower() for ext in ['.xls', '.xlsx', '.csv', '.pdf'])]
        print("NSDL files:", nsdl_files[:10])
except Exception as e:
    print("NSDL error:", e)
