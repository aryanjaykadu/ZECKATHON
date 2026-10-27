import os
import sys
import hashlib
import csv

def check_file_validity(fpath):
    """Verify that file is not empty and not an HTML error page."""
    sz = os.path.getsize(fpath)
    if sz == 0:
        return False, "Empty file (0 bytes)"
    
    with open(fpath, "rb") as f:
        head = f.read(512)
        
    ext = os.path.splitext(fpath)[1].lower()
    
    if ext == ".pdf":
        if not head.startswith(b"%PDF-"):
            # Check if it's HTML
            if b"<html" in head.lower() or b"<!doctype" in head.lower():
                return False, f"HTML error page disguised as PDF ({sz:,} bytes)"
            return False, f"Invalid PDF header ({sz:,} bytes)"
        return True, f"Valid PDF ({sz:,} bytes)"
        
    elif ext == ".xml":
        if not (head.startswith(b"<?xml") or head.startswith(b"<")):
            return False, f"Invalid XML header ({sz:,} bytes)"
        return True, f"Valid XML ({sz:,} bytes)"
        
    elif ext in [".xlsx", ".zip"]:
        if not head.startswith(b"PK\x03\x04"):
            return False, f"Invalid ZIP/XLSX header ({sz:,} bytes)"
        return True, f"Valid XLSX/ZIP ({sz:,} bytes)"
        
    elif ext == ".xls":
        # Legacy binary OLE2 or HTML/XML table exported as .xls
        if head.startswith(b"\xd0\xcf\x11\xe0"):
            return True, f"Valid binary Excel XLS ({sz:,} bytes)"
        elif b"<html" in head.lower() or b"<?xml" in head.lower() or b"<table" in head.lower():
            return True, f"Valid HTML/XML Excel table ({sz:,} bytes)"
        return True, f"XLS file ({sz:,} bytes)"
        
    elif ext == ".csv":
        return True, f"CSV file ({sz:,} bytes)"
        
    elif ext == ".html":
        return True, f"HTML document ({sz:,} bytes)"
        
    return True, f"File ({sz:,} bytes)"

# Traverse data/raw
summary = {}
invalid_files = []

for root, dirs, files in os.walk("data/raw"):
    if files:
        rel_root = os.path.relpath(root, "data/raw")
        summary[rel_root] = []
        for f in sorted(files):
            fpath = os.path.join(root, f)
            valid, msg = check_file_validity(fpath)
            summary[rel_root].append((f, valid, msg, os.path.getsize(fpath)))
            if not valid:
                invalid_files.append((fpath, msg))

print("="*80)
print("DATA REPOSITORY VERIFICATION SUMMARY")
print("="*80)

total_files = 0
for folder, file_list in summary.items():
    valid_count = sum(1 for _, v, _, _ in file_list if v)
    total_files += len(file_list)
    print(f"\n[{folder}] - {valid_count}/{len(file_list)} valid files")
    for f, v, m, sz in file_list[:3]:
        status = "OK" if v else "FAIL"
        print(f"  [{status}] {f} ({sz:,} bytes) - {m}")
    if len(file_list) > 3:
        print(f"  ... and {len(file_list)-3} more files")

print("\n" + "="*80)
print(f"Total files in repository: {total_files}")
print(f"Invalid / corrupt files: {len(invalid_files)}")
for fpath, err in invalid_files:
    print(f"  FAILED: {fpath} -> {err}")
print("="*80)
