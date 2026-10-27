# Master download script for CDSL annual reports.
# Run from the project root.
import sys, os
sys.path.insert(0, os.getcwd())
from download_utils import download_file, log_missing

# ============================================================
# CDSL Annual Reports  (extracted from cdslindia.com HTML)
# ============================================================
CDSL_BASE = "https://www.cdslindia.com/Downloads/InvestorRels/AnnualReports/"
CDSL_REPORTS = {
    "FY2025-26": "Integrated Annual Report 2025-2026.pdf",
    "FY2024-25": "CDSL_IR25_Final.pdf",
    "FY2023-24": "CDSL Annual Report-23-24.pdf",
    "FY2022-23": "Annual Report 2022-23.pdf",
    "FY2021-22": "87993 CDSL Annual Report.pdf",
    "FY2020-21": "81470_CDSL AR 2020-21_E-Mail Version.pdf",
}

print("=" * 60)
print("CDSL Annual Reports")
print("=" * 60)
for fy, fname in CDSL_REPORTS.items():
    url = CDSL_BASE + fname.replace(" ", "%20")
    dest = os.path.join("data", "raw", "cdsl", "annual_reports", f"CDSL_AR_{fy}.pdf")
    ok = download_file(
        url, dest, "CDSL", "annual_report",
        page_title="CDSL Annual Reports",
        pub_date=fy,
        notes=f"Fiscal year {fy}",
        referer="https://www.cdslindia.com/InvestorRels/AnnualReports.html"
    )
    if not ok:
        log_missing("CDSL", "annual_report", f"Annual Report {fy}", "1 - direct URL failed",
                    "https://www.cdslindia.com/InvestorRels/AnnualReports.html")

print("\nDone with CDSL annual reports.")
