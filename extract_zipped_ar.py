import os
import zipfile
import hashlib
import csv

files = [
    r"data/raw/bse/annual_reports/BSE_AR_FY2022-23.pdf",
    r"data/raw/cams/annual_reports/CAMS_AR_FY2021-22.pdf",
    r"data/raw/cams/annual_reports/CAMS_AR_FY2022-23.pdf",
    r"data/raw/kfin/annual_reports/KFINTECH_AR_FY2022-23.pdf"
]

for fpath in files:
    if zipfile.is_zipfile(fpath):
        print(f"Extracting PDF from ZIP: {fpath}")
        with zipfile.ZipFile(fpath, "r") as z:
            pdf_names = [n for n in z.namelist() if n.lower().endswith(".pdf")]
            if pdf_names:
                pdf_data = z.read(pdf_names[0])
                with open(fpath, "wb") as out:
                    out.write(pdf_data)
                sz = os.path.getsize(fpath)
                sha = hashlib.sha256(pdf_data).hexdigest()
                print(f"  Extracted {pdf_names[0]} -> {sz:,} bytes (SHA: {sha[:16]}...)")
            else:
                print(f"  No PDF inside {fpath}")

print("Extraction complete.")
