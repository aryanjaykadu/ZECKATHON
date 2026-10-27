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

for comp_dir, symbol in COMPANIES.items():
    print(f"\n{'='*60}")
    print(f"Processing Investor Presentations & Transcripts for {symbol} ({comp_dir})")
    print(f"{'='*60}")
    
    url = f"https://www.nseindia.com/api/corporate-announcements?index=equities&symbol={symbol}"
    r = session.get(url, timeout=20)
    if r.status_code != 200:
        print(f"Failed to fetch announcements for {symbol}: status {r.status_code}")
        continue
        
    announcements = r.json()
    
    presentations = []
    transcripts = []
    
    for a in announcements:
        dt_raw = a.get("dt", "")
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
        
        if not file_url or not file_url.lower().endswith(".pdf"):
            continue
            
        date_str = pub_dt.strftime("%Y-%m-%d")
        
        # Check for investor presentations
        if any(kw in text for kw in ["investor presentation", "presentation on financial", "earnings presentation", "corporate presentation", "presentation for the financial", "analyst presentation"]):
            # Avoid schedules or notices
            if not any(skip in text for skip in ["schedule of meet", "notice of", "prior intimation"]):
                presentations.append((pub_dt, date_str, desc, att, file_url))
                
        # Check for transcripts
        if any(kw in text for kw in ["transcript", "concall transcript", "call transcript", "audio recording", "conference call recording", "transcript of conference call", "transcript of earnings call", "earnings call transcript"]):
            if not any(skip in text for skip in ["schedule of meet", "intimation of concall", "intimation of conference call", "prior intimation"]):
                transcripts.append((pub_dt, date_str, desc, att, file_url))
                
    # Sort descending
    presentations.sort(key=lambda x: x[0], reverse=True)
    transcripts.sort(key=lambda x: x[0], reverse=True)
    
    print(f"Found {len(presentations)} presentations, {len(transcripts)} transcripts for {symbol}")
    
    # Download presentations (up to 8)
    pres_count = 0
    seen_pres = set()
    for pub_dt, date_str, desc, att, file_url in presentations:
        if date_str in seen_pres:
            continue
        dest = os.path.join("data", "raw", comp_dir, "investor_presentations", f"{symbol}_Presentation_{date_str}.pdf")
        print(f"  [Presentation {pres_count+1}] {date_str}: {att[:70]}")
        ok = download_file(
            file_url, dest, symbol, "investor_presentation",
            page_title=f"NSE Announcement - {symbol} {desc}",
            pub_date=date_str, notes=att[:100],
            referer="https://www.nseindia.com"
        )
        if ok:
            pres_count += 1
            seen_pres.add(date_str)
        if pres_count >= 8:
            break
            
    if pres_count < 8:
        log_missing(symbol, "investor_presentations", f"Downloaded {pres_count}/8 presentations", "NSE corporate announcements", url)
        
    # Download transcripts (up to 8)
    trans_count = 0
    seen_trans = set()
    for pub_dt, date_str, desc, att, file_url in transcripts:
        if date_str in seen_trans:
            continue
        dest = os.path.join("data", "raw", comp_dir, "earnings_transcripts", f"{symbol}_Transcript_{date_str}.pdf")
        print(f"  [Transcript {trans_count+1}] {date_str}: {att[:70]}")
        ok = download_file(
            file_url, dest, symbol, "earnings_transcript",
            page_title=f"NSE Announcement - {symbol} {desc}",
            pub_date=date_str, notes=att[:100],
            referer="https://www.nseindia.com"
        )
        if ok:
            trans_count += 1
            seen_trans.add(date_str)
        if trans_count >= 8:
            break
            
    if trans_count < 8:
        log_missing(symbol, "earnings_transcripts", f"Downloaded {trans_count}/8 transcripts", "NSE corporate announcements", url)
