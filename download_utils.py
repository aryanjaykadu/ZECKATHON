"""Utility functions for downloading and logging files."""
import hashlib, csv, os, time, requests
from datetime import datetime

LOG_FILE = os.path.join("data", "download_log.csv")
MISSING_FILE = os.path.join("data", "MISSING.md")
TODAY = datetime.now().strftime("%Y-%m-%d")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/pdf,application/octet-stream,*/*",
}

def download_file(url, dest_path, entity, data_type, page_title="", pub_date="", notes="", referer=None):
    """Download a file, compute sha256, log it. Returns True on success."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    headers = HEADERS.copy()
    if referer:
        headers["Referer"] = referer
    
    try:
        r = requests.get(url, headers=headers, timeout=60, stream=True)
        r.raise_for_status()
        
        # Check if we got HTML error page instead of expected file
        ct = r.headers.get("Content-Type", "")
        if "text/html" in ct and data_type != "html_page":
            print(f"  WARNING: Got HTML instead of expected file for {url}")
            # Still save it but note it
            notes += " [GOT HTML - may be error page]"
        
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        
        sha = hashlib.sha256(open(dest_path, "rb").read()).hexdigest()
        fsize = os.path.getsize(dest_path)
        fname = os.path.basename(dest_path)
        
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([fname, entity, data_type, url, page_title, pub_date, TODAY, sha, f"Size={fsize}B. {notes}"])
        
        print(f"  OK: {fname} ({fsize:,} bytes)")
        time.sleep(1)  # Rate limit
        return True
    except Exception as e:
        print(f"  FAILED: {url} -> {e}")
        return False

def log_missing(entity, data_type, description, attempts, where_to_find):
    """Append to MISSING.md."""
    with open(MISSING_FILE, "a", encoding="utf-8") as f:
        f.write(f"| {entity} | {data_type} | {description} | {attempts} | {where_to_find} |\n")
    print(f"  MISSING logged: {entity}/{data_type}: {description}")

if __name__ == "__main__":
    print("download_utils ready.")
