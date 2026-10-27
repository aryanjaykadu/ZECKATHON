import os
import sys
from pathlib import Path
import pypdf
import openpyxl
import pandas as pd
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import RAW_DATA_DIR, CUTOFF_DATE, assert_before_cutoff

def audit_pdf(fpath):
    """Verify that file is a non-empty, readable PDF with at least 1 page."""
    sz = os.path.getsize(fpath)
    if sz == 0:
        return False, "Empty file (0 bytes)"
    try:
        reader = pypdf.PdfReader(fpath)
        num_pages = len(reader.pages)
        if num_pages == 0:
            return False, "PDF contains 0 pages"
        # Try reading first page
        p0 = reader.pages[0].extract_text()
        return True, f"Valid PDF, {num_pages} pages ({sz:,} bytes)"
    except Exception as e:
        return False, f"Corrupt PDF or read error: {e}"

def audit_xlsx(fpath):
    """Verify that file is a valid openable Excel workbook."""
    sz = os.path.getsize(fpath)
    if sz == 0:
        return False, "Empty file (0 bytes)"
    try:
        wb = openpyxl.load_workbook(fpath, read_only=True)
        sheets = wb.sheetnames
        wb.close()
        return True, f"Valid Excel, {len(sheets)} sheets ({sz:,} bytes)"
    except Exception as e:
        return False, f"Corrupt Excel or read error: {e}"

def audit_csv(fpath):
    """Verify that file is a valid CSV and assert max date <= CUTOFF_DATE if price data."""
    sz = os.path.getsize(fpath)
    if sz == 0:
        return False, "Empty file (0 bytes)"
    try:
        df = pd.read_csv(fpath)
        if df.empty:
            return False, "Empty CSV dataframe"
        # Check date column if present
        date_cols = [c for c in df.columns if 'date' in c.lower()]
        if date_cols:
            dcol = date_cols[0]
            max_dt = pd.to_datetime(df[dcol]).max()
            assert_before_cutoff(max_dt.to_pydatetime(), context=f"{fpath}")
            return True, f"Valid CSV, {len(df)} rows, max date {max_dt.strftime('%Y-%m-%d')} <= {CUTOFF_DATE}"
        return True, f"Valid CSV, {len(df)} rows ({sz:,} bytes)"
    except Exception as e:
        return False, f"CSV error: {e}"

def run_full_audit():
    """Perform comprehensive audit of data/raw directory."""
    results = {}
    total_files = 0
    corrupt_files = []

    for root, dirs, files in os.walk(RAW_DATA_DIR):
        if not files:
            continue
        rel = os.path.relpath(root, RAW_DATA_DIR)
        results[rel] = []
        for f in sorted(files):
            total_files += 1
            fpath = os.path.join(root, f)
            ext = os.path.splitext(f)[1].lower()
            if ext == ".pdf":
                ok, msg = audit_pdf(fpath)
            elif ext in [".xlsx", ".xlsm"]:
                ok, msg = audit_xlsx(fpath)
            elif ext == ".csv":
                ok, msg = audit_csv(fpath)
            elif ext in [".xml", ".html", ".xls"]:
                sz = os.path.getsize(fpath)
                ok = sz > 0
                msg = f"Non-empty {ext} file ({sz:,} bytes)"
            else:
                sz = os.path.getsize(fpath)
                ok = sz > 0
                msg = f"File ({sz:,} bytes)"
            
            results[rel].append((f, ok, msg, os.path.getsize(fpath)))
            if not ok:
                corrupt_files.append((fpath, msg))

    return results, total_files, corrupt_files

if __name__ == "__main__":
    results, total, corrupt = run_full_audit()
    print(f"Audited {total} files across {len(results)} directories.")
    print(f"Corrupt / Failed: {len(corrupt)}")
    for f, msg in corrupt:
        print(f"  FAILED: {f} -> {msg}")
