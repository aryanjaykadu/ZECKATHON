import os
import sys
import requests
import re
import time

sys.path.insert(0, os.getcwd())
from download_utils import download_file, log_missing

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

dest_dir = os.path.join("data", "raw", "industry", "amfi")
os.makedirs(dest_dir, exist_ok=True)

# Fetch listing of AMFI monthly excel files
print("Fetching AMFI monthly directory page...")
r = requests.get("https://www.amfiindia.com/research-information/amfi-monthly", headers=headers, timeout=20)
links = re.findall(r'href=[\'"]([^\'"]+\.xls[^\'"]*)[\'"]', r.text, re.IGNORECASE)

print(f"Total excel files on AMFI page: {len(links)}")

# We need the last 5 years (60 months) up to September 2026 (cutoff Oct 26, 2026)
target_links = links[:60]
print(f"Downloading latest {len(target_links)} months (5 years)...")

downloaded = 0
for url in target_links:
    fname = os.path.basename(url.split("?")[0])
    # Extract month/year from fname e.g. amsep2026repo.xls -> amfi_monthly_2026_09.xls
    dest_path = os.path.join(dest_dir, fname)
    
    ok = download_file(
        url,
        dest_path,
        "AMFI",
        "industry_amfi_monthly",
        page_title="AMFI Monthly Data (AUM & Folios)",
        pub_date=fname,
        notes=f"Scheme-wise AUM, folios, sales, redemptions, net inflows",
        referer="https://www.amfiindia.com/research-information/amfi-monthly"
    )
    if ok:
        downloaded += 1
    else:
        log_missing("AMFI", "industry_amfi", f"Monthly report {fname}", "Direct download failed", url)
    time.sleep(0.5)

print(f"\nAMFI download finished: {downloaded}/{len(target_links)} files downloaded.")
