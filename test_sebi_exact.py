import requests
import re

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})

url = "https://www.sebi.gov.in/legal/circulars/oct-2024/measures-to-strengthen-equity-index-derivatives-framework-for-increased-investor-protection-and-market-stability_87291.html"
r = session.get(url, timeout=15)
print("SEBI Oct 1 (87291):", r.status_code, len(r.content))
if r.status_code == 200:
    pdfs = re.findall(r'href=[\'"]([^\'"]+\.pdf[^\'"]*)[\'"]', r.text)
    print("PDFs in href:", pdfs)
    iframes = re.findall(r'src=[\'"]([^\'"]+\.pdf[^\'"]*)[\'"]', r.text)
    print("PDFs in src:", iframes)
