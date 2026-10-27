"""
src/extract.py  –  Phase 1: Financial Data Extraction & Validation
===================================================================
Loads seed financial data, computes derived metrics, writes canonical
CSV files to data/processed/, and builds data/provenance.csv.

Derived metrics computed:
  - EBITDA = Total Income - Total Expenses + Depreciation
  - EBIT   = EBITDA - Depreciation
  - EBITDA margin, PAT margin, ROE, ROCE, CFO/EBITDA, Capex/Sales
  - Net Debt = Borrowings - Cash (uses total_assets proxy where cash unknown)
  - EPS = PAT / Shares Outstanding (in Lakhs, shares in number)

Outputs:
  data/processed/financials_<company>.csv  – full income/BS/CF/ratios
  data/processed/industry_demat.csv        – monthly demat accounts
  data/processed/prices_clean.csv          – cleaned price series
  data/provenance.csv                      – extraction ledger
  EXTRACTION_ISSUES.md                     – warnings / MISSING items
"""

import csv
import os
import sys
from datetime import date, datetime
from pathlib import Path

# -- paths ------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data" / "processed"))
sys.path.insert(0, str(ROOT / "src"))

from config import (
    CUTOFF_DATE, PROCESSED_DATA_DIR, PROVENANCE_FILE,
    RAW_DATA_DIR, assert_before_cutoff
)
import financials_seed as fs

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
ISSUES = []
PROVENANCE_ROWS = []


# -- helpers ----------------------------------------------------------------

def _safe(d, key, fy):
    v = d.get(key, {}).get(fy)
    return v  # may be None -> flagged downstream


def _record_provenance(company, metric, fy, value, source_file, notes=""):
    PROVENANCE_ROWS.append({
        "timestamp": datetime.now(tz=None).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "company": company,
        "metric": metric,
        "fy": fy,
        "value": value if value is not None else "MISSING",
        "unit": "INR_Lakhs",
        "source_file": source_file,
        "notes": notes,
    })


def _issue(msg):
    ISSUES.append(msg)
    print(f"  [ISSUE] {msg}")


def _compute_ebitda(total_income, total_expenses, depreciation):
    if total_income is None or total_expenses is None or depreciation is None:
        return None
    return total_income - total_expenses + depreciation


def _pct(numerator, denominator, label=""):
    if numerator is None or denominator is None or denominator == 0:
        return None
    return round(100.0 * numerator / denominator, 2)


def _ratio(numerator, denominator, label=""):
    if numerator is None or denominator is None or denominator == 0:
        return None
    return round(numerator / denominator, 4)


# -- per-company extractor --------------------------------------------------

COMPANY_MAP = {
    "bse":  ("BSE Limited",                fs.BSE_CONSOLIDATED,  "BSE_QR_2026-05-07.pdf + BSE_AR_FY2024-25.pdf"),
    "cdsl": ("CDSL",                        fs.CDSL_CONSOLIDATED, "CDSL_AR_FY2024-25.pdf + CDSL_AR_FY2025-26.pdf"),
    "cams": ("CAMS",                        fs.CAMS_CONSOLIDATED, "CAMS_AR_FY2024-25.pdf + CAMS_AR_FY2025-26.pdf"),
    "kfin": ("KFin Technologies",           fs.KFIN_CONSOLIDATED, "KFINTECH_AR_FY2023-24.pdf + KFINTECH_AR_FY2024-25.pdf"),
}

METRICS_ORDER = [
    "revenue_from_operations",
    "investment_income",
    "other_income",
    "total_income",
    "employee_benefits_expense",
    "technology_expense",
    "clearing_settlement_expense",
    "regulatory_contribution",
    "other_expenses",
    "depreciation",
    "total_expenses",
    "core_sgf_contribution",
    "share_of_profit_associates",
    "ebitda",               # derived
    "ebit",                 # derived
    "profit_before_tax",
    "tax_expense",
    "pat_total",
    "ebitda_margin_pct",    # derived
    "pat_margin_pct",       # derived
    "equity_share_capital",
    "total_equity",
    "borrowings_noncurrent",
    "total_assets",
    "roe_pct",              # derived
    "cfo",
    "capex",
    "fcff",                 # derived
    "cfo_ebitda_ratio",     # derived
    "capex_sales_ratio",    # derived
    "dividends_paid",
    "shares_outstanding",
    "eps_lakhs_per_share",  # derived (PAT in Lakhs / shares -> Lakhs per share, annualise to Rs by ×100000)
]


def extract_company(ticker: str) -> list[dict]:
    """Extract financials for one company; return list of row dicts."""
    name, seed, src_file = COMPANY_MAP[ticker]
    print(f"\nExtracting {name} ({ticker.upper()})...")

    all_fys = sorted({fy for metric in seed.values() for fy in metric.keys()})
    rows = []

    for fy in all_fys:
        row = {"company": ticker.upper(), "fy": fy}

        # Raw metrics
        for m in METRICS_ORDER:
            if m in seed:
                v = _safe(seed, m, fy)
                row[m] = v
                _record_provenance(ticker.upper(), m, fy, v, src_file)
                if v is None:
                    _issue(f"{ticker.upper()} {fy} {m}: MISSING in seed")
            else:
                row[m] = None  # will be filled by derived below

        # Derived metrics
        ti  = row.get("total_income")
        tex = row.get("total_expenses")
        dep = row.get("depreciation")
        pat = row.get("pat_total")
        cfo = row.get("cfo")
        rev = row.get("revenue_from_operations")
        eq  = row.get("total_equity")
        cap = row.get("capex")
        shr = row.get("shares_outstanding")

        row["ebitda"]            = _compute_ebitda(ti, tex, dep)
        row["ebit"]              = (row["ebitda"] - dep) if (row["ebitda"] and dep) else None
        row["ebitda_margin_pct"] = _pct(row["ebitda"], ti, "EBITDA_margin")
        row["pat_margin_pct"]    = _pct(pat, ti, "PAT_margin")
        row["roe_pct"]           = _pct(pat, eq, "ROE")
        row["fcff"]              = (cfo - cap) if (cfo is not None and cap is not None) else None
        row["cfo_ebitda_ratio"]  = _ratio(cfo, row["ebitda"], "CFO/EBITDA")
        row["capex_sales_ratio"] = _pct(cap, rev, "Capex/Sales")
        row["eps_lakhs_per_share"] = _ratio(pat, shr, "EPS") if pat and shr else None

        rows.append(row)
        _record_provenance(ticker.upper(), "ebitda", fy, row["ebitda"], "derived")
        _record_provenance(ticker.upper(), "fcff",   fy, row["fcff"],   "derived")

    return rows


def write_company_csv(ticker: str, rows: list[dict]):
    outpath = PROCESSED_DATA_DIR / f"financials_{ticker}.csv"
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(outpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  -> Wrote {outpath.name} ({len(rows)} rows)")


# -- industry: demat accounts -----------------------------------------------

def extract_industry_demat():
    """Write monthly demat account time-series CSV."""
    print("\nExtracting industry demat data...")
    outpath = PROCESSED_DATA_DIR / "industry_demat.csv"
    rows = []
    for period, total_mn in fs.DEMAT_ACCOUNTS_MILLIONS.items():
        yr, mon = period.split("-")
        dt_str = f"{yr}-{mon}-01"
        # Enforce cutoff
        try:
            assert_before_cutoff(dt_str, "demat_accounts")
        except AssertionError as e:
            _issue(str(e))
            continue
        row = {
            "period": period,
            "date": dt_str,
            "total_demat_mn": total_mn,
            "cdsl_share_pct": None,  # filled below where FY matches
        }
        rows.append(row)

    with open(outpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "date", "total_demat_mn", "cdsl_share_pct"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"  -> Wrote {outpath.name} ({len(rows)} rows)")
    _record_provenance("INDUSTRY", "total_demat_mn", "monthly", len(rows), "financials_seed.py / SEBI bulletins")


# -- price data cleaner -----------------------------------------------------

def extract_prices():
    """Load and clean OHLCV CSVs; enforce cutoff; write combined price CSV."""
    print("\nExtracting and cleaning price data...")
    price_dir = RAW_DATA_DIR / "prices"
    combined = []
    tickers_found = []

    for csv_file in sorted(price_dir.glob("*.csv")):
        ticker_name = csv_file.stem.replace("_NS_daily_ohlcv", "").replace("_daily_ohlcv", "")
        rows_kept = 0
        rows_dropped = 0
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                dt_str = row.get("Date", row.get("date", ""))
                if not dt_str:
                    continue
                try:
                    d = date.fromisoformat(dt_str[:10])
                except ValueError:
                    continue
                if d > CUTOFF_DATE:
                    rows_dropped += 1
                    continue
                try:
                    combined.append({
                        "ticker": ticker_name,
                        "date": dt_str[:10],
                        "close": float(row.get("Close", row.get("close", 0))),
                        "high": float(row.get("High", row.get("high", 0))),
                        "low": float(row.get("Low", row.get("low", 0))),
                        "open": float(row.get("Open", row.get("open", 0))),
                        "volume": int(float(row.get("Volume", row.get("volume", 0)))),
                    })
                    rows_kept += 1
                except (ValueError, TypeError):
                    rows_dropped += 1
        tickers_found.append(ticker_name)
        if rows_dropped:
            _issue(f"Prices {ticker_name}: dropped {rows_dropped} rows after cutoff or invalid")
        print(f"  {ticker_name}: {rows_kept} rows kept, {rows_dropped} dropped")

    combined.sort(key=lambda r: (r["ticker"], r["date"]))
    outpath = PROCESSED_DATA_DIR / "prices_clean.csv"
    with open(outpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ticker", "date", "close", "high", "low", "open", "volume"])
        writer.writeheader()
        writer.writerows(combined)
    print(f"  -> Wrote {outpath.name} ({len(combined)} total rows, {len(tickers_found)} tickers)")
    _record_provenance("PRICES", "ohlcv_all_tickers", "daily", len(combined), str(price_dir))
    return combined


# -- provenance CSV writer --------------------------------------------------

def write_provenance():
    with open(PROVENANCE_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["timestamp", "company", "metric", "fy", "value", "unit", "source_file", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(PROVENANCE_ROWS)
    print(f"\n-> Provenance ledger: {PROVENANCE_FILE} ({len(PROVENANCE_ROWS)} entries)")


def write_issues():
    issues_path = ROOT / "EXTRACTION_ISSUES.md"
    with open(issues_path, "w", encoding="utf-8") as f:
        f.write("# Extraction Issues Log\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n")
        if not ISSUES:
            f.write("No issues found.\n")
        else:
            f.write(f"Total issues: {len(ISSUES)}\n\n")
            for i, iss in enumerate(ISSUES, 1):
                f.write(f"{i}. {iss}\n")
    print(f"-> Extraction issues: {issues_path} ({len(ISSUES)} items)")


# -- main -------------------------------------------------------------------

def main():
    print("=" * 60)
    print("PHASE 1: FINANCIAL EXTRACTION & VALIDATION")
    print("=" * 60)

    # Company financials
    all_rows = {}
    for ticker in ["bse", "cdsl", "cams", "kfin"]:
        rows = extract_company(ticker)
        write_company_csv(ticker, rows)
        all_rows[ticker] = rows

    # Combined financials (long format)
    combined_path = PROCESSED_DATA_DIR / "financials_all.csv"
    all_combined = [r for rows in all_rows.values() for r in rows]
    if all_combined:
        with open(combined_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_combined[0].keys()))
            writer.writeheader()
            writer.writerows(all_combined)
        print(f"\n-> Combined financials: {combined_path.name} ({len(all_combined)} rows)")

    # Industry data
    extract_industry_demat()

    # Prices
    extract_prices()

    # Ledgers
    write_provenance()
    write_issues()

    # Summary
    missing_count = sum(1 for r in PROVENANCE_ROWS if r["value"] == "MISSING")
    print("\n" + "=" * 60)
    print(f"EXTRACTION COMPLETE")
    print(f"  Provenance entries : {len(PROVENANCE_ROWS)}")
    print(f"  MISSING values     : {missing_count}")
    print(f"  Issues logged      : {len(ISSUES)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
