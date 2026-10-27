import os
import sys
import re
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

# We want the last 8 quarters of financial results.
# Target quarters ending:
# Jun 30, 2026 (Q1 FY27)
# Mar 31, 2026 (Q4 FY26)
# Dec 31, 2025 (Q3 FY26)
# Sep 30, 2025 (Q2 FY26)
# Jun 30, 2025 (Q1 FY26)
# Mar 31, 2025 (Q4 FY25)
# Dec 31, 2024 (Q3 FY25)
# Sep 30, 2024 (Q2 FY25)
# (Also Sep 30, 2026 / Q2 FY27 if available on or before Oct 26, 2026, e.g., KFintech announced on Oct 26, 2026)

for comp_dir, symbol in COMPANIES.items():
    print(f"\n{'='*60}")
    print(f"Finding & Downloading Quarterly Results for {symbol} ({comp_dir})")
    print(f"{'='*60}")
    
    url = f"https://www.nseindia.com/api/corporate-announcements?index=equities&symbol={symbol}"
    r = session.get(url, timeout=20)
    if r.status_code != 200:
        print(f"Failed to fetch announcements for {symbol}: status {r.status_code}")
        continue
        
    announcements = r.json()
    
    # Filter candidates
    candidates = []
    for a in announcements:
        dt_raw = a.get("dt", "")
        # Parse dt: DDMMYYYYHHMMSS
        try:
            pub_dt = datetime.strptime(dt_raw[:8], "%d%m%Y")
        except:
            continue
            
        if pub_dt > CUTOFF:
            continue
            
        desc = a.get("desc", "")
        att = a.get("attchmntText", "")
        text = (desc + " " + att).lower()
        file_url = a.get("attchmntFile", "")
        
        if not file_url:
            continue
            
        # We want Outcome of Board Meeting with financial results or Financial Result Updates
        if "financial result" in text or "outcome of board meeting" in text:
            if any(skip in text for skip in ["trading window", "notice of board meeting", "prior intimation", "schedule of meet", "investor meet", "analysts/institutional", "appointment", "press release", "media release", "newspaper", "presentation"]):
                # Skip pure press releases or meetings unless they are the primary submission
                if "outcome of board meeting" not in text and "submitted to the exchange, the financial results" not in text:
                    continue
            
            # Further verify it is results
            if "financial results" in text or "submitted to the exchange, the financial results" in text or "outcome of board meeting" in text:
                candidates.append((pub_dt, dt_raw, desc, att, file_url))
                
    print(f"Found {len(candidates)} candidate announcements for {symbol}")
    
    # Sort descending by date
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    # Identify unique quarterly results submissions (limit to last 8 quarters)
    downloaded_count = 0
    seen_dates = set()
    
    for pub_dt, dt_raw, desc, att, file_url in candidates:
        # Check if text actually discusses financial results for a period
        lower_att = att.lower()
        if not ("financial results" in lower_att or "period ended" in lower_att or "quarter ended" in lower_att or "financial year ended" in lower_att or "half year ended" in lower_att or "outcome of board meeting" in desc.lower()):
            continue
            
        date_str = pub_dt.strftime("%Y-%m-%d")
        if date_str in seen_dates:
            continue
            
        # Determine quarter label from text if possible
        # e.g. Jun 30, 2026 -> Q1_FY27
        fname_label = f"{symbol}_QR_{date_str}"
        ext = ".pdf" if file_url.lower().endswith(".pdf") else os.path.splitext(file_url)[1] or ".pdf"
        dest_path = os.path.join("data", "raw", comp_dir, "quarterly_results", f"{fname_label}{ext}")
        
        print(f"  [{downloaded_count+1}/8] Downloading {pub_dt.strftime('%d-%b-%Y')}: {att[:80]}")
        ok = download_file(
            file_url,
            dest_path,
            symbol,
            "quarterly_result",
            page_title=f"NSE Announcement - {symbol} {desc}",
            pub_date=date_str,
            notes=f"{att[:100]} | Date: {date_str}",
            referer="https://www.nseindia.com/companies-listing/corporate-filings-announcements"
        )
        if ok:
            downloaded_count += 1
            seen_dates.add(date_str)
            
        if downloaded_count >= 8:
            break
            
    print(f"Successfully downloaded {downloaded_count} quarterly results for {symbol}")
    if downloaded_count < 8:
        log_missing(symbol, "quarterly_results", f"Only {downloaded_count}/8 quarters downloaded", "Automated NSE announcement extraction", "https://www.nseindia.com")
