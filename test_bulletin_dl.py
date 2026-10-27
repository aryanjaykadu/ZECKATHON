import requests
import os
import sys

sys.path.insert(0, os.getcwd())
from download_utils import download_file

url = "https://www.sebi.gov.in/sebi_data/commondocs/sep-2026/Bulletins%20Aug-26%20I_p.xlsx"
dest = "data/raw/industry/derivatives_turnover/SEBI_Bulletin_Aug_2026_Annexure_Tables.xlsx"

ok = download_file(
    url, dest, "SEBI", "industry_derivatives_demat",
    page_title="SEBI Bulletin August 2026 Annexure Tables",
    pub_date="2026-08-31",
    notes="Contains monthly derivatives turnover (NSE + BSE) and depository accounts (CDSL + NSDL)",
    referer="https://www.sebi.gov.in"
)
print("Download result:", ok)
