import requests
import re
from bs4 import BeautifulSoup
import os
import sys

sys.path.insert(0, os.getcwd())
from download_utils import download_file, log_missing

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

sebi_pages = [
    {
        "title": "SEBI Circular - True to Label Charges (01-Jul-2024)",
        "url": "https://www.sebi.gov.in/legal/circulars/jul-2024/charges-levied-by-market-infrastructure-institutions-true-to-label_84795.html",
        "date": "2024-07-01",
        "fname": "SEBI_Circular_True_to_Label_Charges_2024-07-01.pdf"
    },
    {
        "title": "SEBI Circular - Measures to Strengthen Equity Index Derivatives Framework (01-Oct-2024)",
        "url": "https://www.sebi.gov.in/legal/circulars/oct-2024/measures-to-strengthen-equity-index-derivatives-framework-for-increased-investor-protection-and-market-stability_87029.html",
        "date": "2024-10-01",
        "fname": "SEBI_Circular_Index_Derivatives_Framework_2024-10-01.pdf"
    },
    {
        "title": "SEBI Consultation Paper - Index Derivatives Framework (30-Jul-2024)",
        "url": "https://www.sebi.gov.in/reports-and-statistics/reports/jul-2024/consultation-paper-on-measures-to-strengthen-index-derivatives-framework-for-increased-investor-protection-and-market-stability_85304.html",
        "date": "2024-07-30",
        "fname": "SEBI_Consultation_Paper_Index_Derivatives_2024-07-30.pdf"
    }
]

dest_dir = os.path.join("data", "raw", "regulation", "sebi")
os.makedirs(dest_dir, exist_ok=True)

for item in sebi_pages:
    print(f"\nFetching page: {item['title']}")
    try:
        r = requests.get(item['url'], headers=headers, timeout=20)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            # Save HTML page as reference
            html_name = item['fname'].replace('.pdf', '.html')
            with open(os.path.join(dest_dir, html_name), "w", encoding="utf-8") as f:
                f.write(r.text)
                
            # Look for iframe or link pointing to PDF
            pdf_urls = re.findall(r'href=[\'"]([^\'"]+\.pdf[^\'"]*)[\'"]', r.text, re.IGNORECASE)
            iframe_urls = re.findall(r'src=[\'"]([^\'"]+\.pdf[^\'"]*)[\'"]', r.text, re.IGNORECASE)
            
            candidates = pdf_urls + iframe_urls
            print("Found candidates:", candidates)
            
            pdf_download_url = None
            if candidates:
                for c in candidates:
                    if "sebi.gov.in" in c or c.startswith("/"):
                        pdf_download_url = c if c.startswith("http") else "https://www.sebi.gov.in" + c
                        break
                if not pdf_download_url:
                    pdf_download_url = candidates[0] if candidates[0].startswith("http") else "https://www.sebi.gov.in" + candidates[0]
                    
            if pdf_download_url:
                print(f"Downloading PDF from: {pdf_download_url}")
                dest_path = os.path.join(dest_dir, item['fname'])
                download_file(
                    pdf_download_url, dest_path, "SEBI", "regulation_circular",
                    page_title=item['title'], pub_date=item['date'],
                    notes=f"SEBI Regulation. Page: {item['url']}", referer=item['url']
                )
            else:
                print("No direct PDF link found in HTML. Saved HTML page.")
        else:
            print("Page fetch returned non-200")
            log_missing("SEBI", "regulation", item['title'], "1 - HTTP " + str(r.status_code), item['url'])
    except Exception as e:
        print(f"Error fetching {item['url']}: {e}")
        log_missing("SEBI", "regulation", item['title'], f"Exception: {e}", item['url'])
