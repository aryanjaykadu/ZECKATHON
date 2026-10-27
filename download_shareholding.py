import os
import sys
import requests
import json
from datetime import datetime

sys.path.insert(0, os.getcwd())
from download_utils import download_file, log_missing

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/",
})

COMPANIES = {
    "bse": "BSE",
    "cdsl": "CDSL",
    "cams": "CAMS",
    "kfin": "KFINTECH"
}

CUTOFF = datetime(2026, 10, 26, 23, 59, 59)

# We want shareholding patterns for the last 8 quarters (or available quarters <= CUTOFF)
for comp_dir, symbol in COMPANIES.items():
    print(f"\n{'='*60}")
    print(f"Downloading Shareholding Patterns for {symbol} ({comp_dir})")
    print(f"{'='*60}")
    
    url = f"https://www.nseindia.com/api/corporate-share-holdings-master?index=equities&symbol={symbol}"
    r = session.get(url, timeout=20)
    if r.status_code != 200:
        print(f"Failed to fetch shareholding master for {symbol}: {r.status_code}")
        log_missing(symbol, "shareholding", "Failed to fetch shareholding master", "1 - NSE API error", url)
        continue
        
    items = r.json()
    print(f"Found {len(items)} shareholding entries for {symbol}")
    
    downloaded = 0
    for item in items:
        # Check submission date <= CUTOFF
        sub_dt_str = item.get("submissionDate", "")
        quarter_date_str = item.get("date", "")
        try:
            sub_dt = datetime.strptime(sub_dt_str, "%d-%b-%Y")
        except:
            sub_dt = None
            
        if sub_dt and sub_dt > CUTOFF:
            print(f"  Skipping {sub_dt_str} (after cutoff)")
            continue
            
        xbrl_url = item.get("xbrl", "")
        if not xbrl_url:
            continue
            
        # Format filename: e.g. BSE_SHP_30-SEP-2026.xml
        fname = f"{symbol}_SHP_{quarter_date_str}.xml"
        dest_path = os.path.join("data", "raw", comp_dir, "shareholding", fname)
        
        print(f"  Downloading quarter {quarter_date_str} (submitted {sub_dt_str})")
        ok = download_file(
            xbrl_url,
            dest_path,
            symbol,
            "shareholding_pattern",
            page_title=f"NSE Shareholding Pattern - {symbol} for {quarter_date_str}",
            pub_date=sub_dt_str,
            notes=f"Quarter ending: {quarter_date_str}. Size: {item.get('xbrlFileSize','')}",
            referer="https://www.nseindia.com/companies-listing/corporate-filings-shareholding-pattern"
        )
        if ok:
            downloaded += 1
            
        if downloaded >= 8:
            break
            
    print(f"Downloaded {downloaded} shareholding patterns for {symbol}")
