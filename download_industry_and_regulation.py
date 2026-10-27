import os
import sys
import requests
import shutil

sys.path.insert(0, os.getcwd())
from download_utils import download_file, log_missing

# ==============================================================================
# 1. SEBI Regulations (Circulars & Notices)
# ==============================================================================
reg_dir = os.path.join("data", "raw", "regulation", "sebi")
os.makedirs(reg_dir, exist_ok=True)

print("="*60)
print("Downloading SEBI Regulation Circulars & Notices")
print("="*60)

reg_files = [
    {
        "url": "https://nsearchives.nseindia.com/content/circulars/FA64232.pdf",
        "dest": os.path.join(reg_dir, "SEBI_MII_Charges_True_to_Label_NSE_FA_64232_2024-09-27.pdf"),
        "entity": "SEBI/NSE",
        "type": "regulation_circular",
        "title": "SEBI True to Label MII Charges - NSE Circular FA64232",
        "pub_date": "2024-09-27",
        "notes": "Implements SEBI Circular SEBI/HO/MRD/TPD-1/P/CIR/2024/92 (Charges levied by MIIs - True to Label)"
    },
    {
        "url": "https://nsearchives.nseindia.com/content/circulars/FAOP64506.pdf",
        "dest": os.path.join(reg_dir, "SEBI_Index_Derivatives_Weekly_Expiry_Discontinuation_NSE_FAOP_64506_2024-10-10.pdf"),
        "entity": "SEBI/NSE",
        "type": "regulation_circular",
        "title": "SEBI Equity Index Derivatives Framework - Rationalization of Weekly Expiries NSE Circular FAOP64506",
        "pub_date": "2024-10-10",
        "notes": "Implements SEBI Circular SEBI/HO/MRD/TPD-1/P/CIR/2024/132 (Discontinuation of Bank Nifty, Fin Nifty, Midcap Nifty weekly contracts)"
    },
    {
        "url": "https://nsearchives.nseindia.com/content/circulars/FAOP70616.pdf",
        "dest": os.path.join(reg_dir, "SEBI_Index_Derivatives_Lot_Size_Revision_NSE_FAOP_70616_2025.pdf"),
        "entity": "SEBI/NSE",
        "type": "regulation_circular",
        "title": "SEBI Equity Index Derivatives - Revision in Market Lot of Derivative Contracts on Indices",
        "pub_date": "2025",
        "notes": "Implements SEBI Index Derivatives minimum contract value and lot size revision"
    },
    {
        "url": "https://www.bseindia.com/markets/MarketInfo/DispNewNoticesCirculars.aspx?noticeid=20241021-13",
        "dest": os.path.join(reg_dir, "BSE_Notice_20241021-13_BANKEX_Lot_Size_Revision_2024-10-21.html"),
        "entity": "SEBI/BSE",
        "type": "regulation_notice",
        "title": "BSE Notice No. 20241021-13 - Revision in Market Lot Size of BANKEX Contracts",
        "pub_date": "2024-10-21",
        "notes": "Implements SEBI directive revising Bankex lot size from 15 to 30"
    }
]

for item in reg_files:
    download_file(
        item["url"], item["dest"], item["entity"], item["type"],
        page_title=item["title"], pub_date=item["pub_date"],
        notes=item["notes"], referer="https://www.nseindia.com" if "nse" in item["url"] else "https://www.bseindia.com"
    )

# ==============================================================================
# 2. Industry Data: Derivatives Turnover and Demat Accounts (SEBI Bulletin Tables)
# ==============================================================================
print("\n" + "="*60)
print("Downloading SEBI Bulletin Annexure Tables for Derivatives Turnover & Demat Accounts")
print("="*60)

deriv_dir = os.path.join("data", "raw", "industry", "derivatives_turnover")
demat_dir = os.path.join("data", "raw", "industry", "demat")
os.makedirs(deriv_dir, exist_ok=True)
os.makedirs(demat_dir, exist_ok=True)

bulletins = [
    ("https://www.sebi.gov.in/sebi_data/commondocs/sep-2026/Bulletins%20Aug-26%20I_p.xlsx", "SEBI_Bulletin_Aug_2026_Annexure_Tables.xlsx", "2026-08-31"),
    ("https://www.sebi.gov.in/sebi_data/commondocs/jul-2026/Monthly%20SEBI%20Bulletin%2027.07.2026_p.xlsx", "SEBI_Bulletin_Jul_2026_Annexure_Tables.xlsx", "2026-07-31"),
    ("https://www.sebi.gov.in/sebi_data/commondocs/jul-2026/Monthly%20SEBI%20Bulletin%20-%2003.07_p.xlsx", "SEBI_Bulletin_Jun_2026_Annexure_Tables.xlsx", "2026-06-30"),
    ("https://www.sebi.gov.in/sebi_data/commondocs/jun-2026/Monthly%20SEBI%20Bulletin%2012.06_p.xlsx", "SEBI_Bulletin_May_2026_Annexure_Tables.xlsx", "2026-05-31"),
    ("https://www.sebi.gov.in/sebi_data/commondocs/apr-2026/Annexure%20Tables-30.04.2026_p.xlsx", "SEBI_Bulletin_Apr_2026_Annexure_Tables.xlsx", "2026-04-30"),
    ("https://www.sebi.gov.in/sebi_data/commondocs/mar-2026/Annexure%20Tables%20March%202026_p.xlsx", "SEBI_Bulletin_Mar_2026_Annexure_Tables.xlsx", "2026-03-31"),
    ("https://www.sebi.gov.in/sebi_data/commondocs/feb-2026/Sebi%20Annexure%20Table%20%2024%20Feb%202026_p.xlsx", "SEBI_Bulletin_Feb_2026_Annexure_Tables.xlsx", "2026-02-28"),
    ("https://www.sebi.gov.in/sebi_data/commondocs/jan-2026/Annexure%20Tables%20January%202026_p.xlsx", "SEBI_Bulletin_Jan_2026_Annexure_Tables.xlsx", "2026-01-31"),
    ("https://www.sebi.gov.in/sebi_data/commondocs/dec-2025/Monthly%20SEBI%20Bulletin-Dec%20Annexure%20Tables_p.xlsx", "SEBI_Bulletin_Dec_2025_Annexure_Tables.xlsx", "2025-12-31"),
    ("https://www.sebi.gov.in/sebi_data/commondocs/dec-2025/Monthly%20Bulletin%20November_p.xlsx", "SEBI_Bulletin_Nov_2025_Annexure_Tables.xlsx", "2025-11-30"),
    ("https://www.sebi.gov.in/sebi_data/commondocs/oct-2025/October%2025%20Bulletin%20Annexure%20Tables_p.xlsx", "SEBI_Bulletin_Oct_2025_Annexure_Tables.xlsx", "2025-10-31"),
]

for url, fname, pub_date in bulletins:
    dest_deriv = os.path.join(deriv_dir, fname)
    dest_demat = os.path.join(demat_dir, fname)
    
    # Check if already downloaded
    if not os.path.exists(dest_deriv):
        ok = download_file(
            url, dest_deriv, "SEBI", "industry_derivatives_turnover",
            page_title=f"SEBI Bulletin Annexure Tables ({pub_date[:7]})",
            pub_date=pub_date,
            notes="Contains Secondary Market Derivatives Turnover (NSE and BSE)",
            referer="https://www.sebi.gov.in"
        )
    else:
        ok = True
        
    if ok and not os.path.exists(dest_demat):
        shutil.copy(dest_deriv, dest_demat)
        print(f"  Copied to demat directory: {dest_demat}")
