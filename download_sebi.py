import os
import sys
import re
import requests

sys.path.insert(0, os.getcwd())
from download_utils import download_file, log_missing

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# 1. Download SEBI regulations
sebi_dir = os.path.join("data", "raw", "regulation", "sebi")
os.makedirs(sebi_dir, exist_ok=True)

sebi_items = [
    {
        "title": "SEBI Circular: Charges Levied by Market Infrastructure Institutions - True to Label",
        "page_url": "https://www.sebi.gov.in/legal/circulars/jul-2024/charges-levied-by-market-infrastructure-institutions-true-to-label_84795.html",
        "date": "2024-07-01",
        "fname": "SEBI_Circular_True_to_Label_MII_Charges_2024-07-01"
    },
    {
        "title": "SEBI Circular: Measures to Strengthen Equity Index Derivatives Framework",
        "page_url": "https://www.sebi.gov.in/legal/circulars/oct-2024/measures-to-strengthen-equity-index-derivatives-framework-for-increased-investor-protection-and-market-stability_87029.html",
        "date": "2024-10-01",
        "fname": "SEBI_Circular_Equity_Index_Derivatives_Framework_2024-10-01"
    },
    {
        "title": "SEBI Consultation Paper: Measures to Strengthen Index Derivatives Framework",
        "page_url": "https://www.sebi.gov.in/reports-and-statistics/reports/jul-2024/consultation-paper-on-measures-to-strengthen-index-derivatives-framework-for-increased-investor-protection-and-market-stability_85304.html",
        "date": "2024-07-30",
        "fname": "SEBI_Consultation_Paper_Index_Derivatives_2024-07-30"
    }
]

for item in sebi_items:
    print(f"\nProcessing SEBI regulation: {item['title']}")
    try:
        r = requests.get(item['page_url'], headers=headers, timeout=25)
        if r.status_code == 200:
            # Save html
            html_path = os.path.join(sebi_dir, item['fname'] + ".html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(r.text)
            print(f"  Saved HTML: {html_path}")
            
            # Find PDF links
            pdfs = re.findall(r'href=[\'"]([^\'"]+\.pdf[^\'"]*)[\'"]', r.text, re.IGNORECASE)
            if not pdfs:
                pdfs = re.findall(r'src=[\'"]([^\'"]+\.pdf[^\'"]*)[\'"]', r.text, re.IGNORECASE)
                
            if pdfs:
                pdf_url = pdfs[0]
                if not pdf_url.startswith("http"):
                    pdf_url = "https://www.sebi.gov.in" + pdf_url
                pdf_path = os.path.join(sebi_dir, item['fname'] + ".pdf")
                download_file(
                    pdf_url, pdf_path, "SEBI", "regulation_circular",
                    page_title=item['title'], pub_date=item['date'],
                    notes=f"URL: {item['page_url']}", referer=item['page_url']
                )
            else:
                print("  No PDF url extracted from HTML")
        else:
            print(f"  HTTP {r.status_code} for {item['page_url']}")
            log_missing("SEBI", "regulation", item['title'], f"HTTP {r.status_code}", item['page_url'])
    except Exception as e:
        print(f"  Error: {e}")
        log_missing("SEBI", "regulation", item['title'], str(e), item['page_url'])
