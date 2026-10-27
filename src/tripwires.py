"""
src/tripwires.py — Phase 9: Observable Exit Triggers
=====================================================
3 observable monthly triggers with current distance from cutoff.

Outputs:
  outputs/tripwires.csv — exit trigger conditions and distances
"""

import csv
import json
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "data" / "processed"))

from config import CUTOFF_DATE, OUTPUTS_DIR, PROVENANCE_FILE

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

with open(ROOT / "assumptions.yaml", "r") as f:
    ASSUMPTIONS = yaml.safe_load(f)


def load_market_data():
    mkt = {}
    mpath = OUTPUTS_DIR / "market_data.csv"
    if not mpath.exists():
        return mkt
    with open(mpath, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mkt[row["company"]] = row
    return mkt


def load_dcf_results():
    results = {}
    fpath = OUTPUTS_DIR / "dcf_results.csv"
    if not fpath.exists():
        return results
    with open(fpath, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            co = row["company"]
            sc = row["scenario"]
            if co not in results:
                results[co] = {}
            results[co][sc] = {
                "dcf_per_share": float(row["dcf_per_share"]),
            }
    return results


# ============================================================
# TRIPWIRE DEFINITIONS
# ============================================================
# Each company gets 3 observable, monthly-checkable exit triggers.

TRIPWIRES = {
    "BSE": [
        {
            "id": "BSE_TW1",
            "trigger": "Monthly F&O notional turnover falls >40% below FY2026 average for 2 consecutive months",
            "metric": "F&O Premium Turnover (NSE/BSE published monthly)",
            "threshold": "< Rs 15 lakh Cr monthly avg premium turnover",
            "action": "EXIT — derivatives revenue collapse confirms bear thesis",
            "observable": "BSE Monthly Market Summary",
        },
        {
            "id": "BSE_TW2",
            "trigger": "SEBI announces further F&O restrictions beyond Nov-2024 curbs (new lot size hike >Rs 25L, or ban on additional indices)",
            "metric": "SEBI Circular / Press Release",
            "threshold": "Any new restriction published on SEBI website",
            "action": "REDUCE 50% — regulatory regime change invalidates base case",
            "observable": "SEBI circulars database (sebi.gov.in)",
        },
        {
            "id": "BSE_TW3",
            "trigger": "BSE stock price trades >20% below bear-case DCF target for 5 consecutive trading days",
            "metric": "Daily closing price on NSE",
            "threshold": None,  # Filled dynamically
            "action": "REVIEW — either thesis is wrong or opportunity to add",
            "observable": "NSE/BSE daily closing price",
        },
    ],
    "CDSL": [
        {
            "id": "CDSL_TW1",
            "trigger": "Monthly net new demat account openings drop below 1.5 million for 3 consecutive months",
            "metric": "CDSL monthly demat account data (cdsl.com)",
            "threshold": "< 1.5M net additions/month",
            "action": "REDUCE 30% — growth saturation thesis triggered",
            "observable": "CDSL website: Demat Account Statistics",
        },
        {
            "id": "CDSL_TW2",
            "trigger": "SEBI announces depository fee cap or restructuring",
            "metric": "SEBI Circular",
            "threshold": "Any regulatory action on depository charges",
            "action": "EXIT — yield compression is permanent",
            "observable": "SEBI circulars database",
        },
        {
            "id": "CDSL_TW3",
            "trigger": "Monthly secondary market traded value falls >30% below trailing 6-month average",
            "metric": "NSE monthly market activity data",
            "threshold": "< Rs 15 lakh Cr monthly cash segment traded value",
            "action": "REDUCE 30% — transaction revenue decline",
            "observable": "NSE Market Activity Report (monthly)",
        },
    ],
    "CAMS": [
        {
            "id": "CAMS_TW1",
            "trigger": "SEBI announces further TER cut or RTA fee regulation",
            "metric": "SEBI Circular on Mutual Fund TER",
            "threshold": "Any new TER regulation reducing RTA basis-point yield",
            "action": "EXIT — yield compression directly impairs revenue",
            "observable": "SEBI circulars database",
        },
        {
            "id": "CAMS_TW2",
            "trigger": "Loss of a top-5 AMC client (e.g., via M&A or in-housing)",
            "metric": "CAMS quarterly investor presentation / exchange filing",
            "threshold": "Any top-5 AMC announces RTA switch",
            "action": "EXIT — client concentration risk crystallizes",
            "observable": "BSE/NSE corporate announcements",
        },
        {
            "id": "CAMS_TW3",
            "trigger": "Industry MF AUM declines >10% from peak for 2 consecutive months",
            "metric": "AMFI monthly AUM data (amfiindia.com)",
            "threshold": "MF industry AAUM < Rs 55 lakh Cr",
            "action": "REDUCE 30% — AUM-linked revenue declines",
            "observable": "AMFI website monthly data",
        },
    ],
    "KFIN": [
        {
            "id": "KFIN_TW1",
            "trigger": "Key AMC client announces competitive RTA rebid or switch to CAMS",
            "metric": "Exchange filings / KFIN quarterly results",
            "threshold": "Loss of >10% of serviced AUM",
            "action": "EXIT — client churn thesis triggered",
            "observable": "BSE/NSE filings + KFIN investor presentations",
        },
        {
            "id": "KFIN_TW2",
            "trigger": "International revenue growth declines to <10% YoY for 2 quarters",
            "metric": "KFIN quarterly segmental reporting",
            "threshold": "International revenue growth < 10%",
            "action": "REDUCE 30% — international thesis weakens",
            "observable": "KFIN quarterly results on BSE/NSE",
        },
        {
            "id": "KFIN_TW3",
            "trigger": "IPO market freeze (zero IPOs >Rs 500 Cr) for 3+ consecutive months",
            "metric": "SEBI IPO tracker / Chittorgarh IPO data",
            "threshold": "Zero large IPOs for 3 months",
            "action": "REDUCE 20% — issuer solutions revenue cyclicality hits",
            "observable": "SEBI/BSE IPO listing data",
        },
    ],
}


def compute_distances(mkt, dcf):
    """Compute current distance from each tripwire threshold."""
    distances = []
    
    for co, triggers in TRIPWIRES.items():
        price = float(mkt.get(co, {}).get("latest_price", 0) or 0)
        
        for tw in triggers:
            tw_copy = dict(tw)
            
            # BSE_TW3: dynamic threshold based on bear DCF
            if tw["id"] == "BSE_TW3" and "BSE" in dcf:
                bear_target = dcf["BSE"]["bear"]["dcf_per_share"]
                threshold_price = bear_target * 0.80
                tw_copy["threshold"] = f"Price < Rs {threshold_price:,.0f}"
                distance = ((price / threshold_price) - 1) * 100 if threshold_price > 0 else 0
                tw_copy["current_distance_pct"] = round(distance, 1)
                tw_copy["status"] = "SAFE" if distance > 10 else ("WATCH" if distance > 0 else "TRIGGERED")
            else:
                # Qualitative triggers — mark as NOT_TRIGGERED
                tw_copy["current_distance_pct"] = None
                tw_copy["status"] = "NOT_TRIGGERED"
            
            tw_copy["company"] = co
            tw_copy["as_of_date"] = str(CUTOFF_DATE)
            distances.append(tw_copy)
    
    return distances


def main():
    print("=" * 60)
    print("PHASE 9: TRIPWIRES (EXIT TRIGGERS)")
    print("=" * 60)
    
    mkt = load_market_data()
    dcf = load_dcf_results()
    
    distances = compute_distances(mkt, dcf)
    
    for d in distances:
        print(f"\n{d['id']}: {d['trigger']}")
        print(f"  Observable: {d['observable']}")
        print(f"  Threshold: {d.get('threshold', 'See description')}")
        print(f"  Status: {d['status']}", end="")
        if d.get("current_distance_pct") is not None:
            print(f" (Distance: {d['current_distance_pct']:+.1f}%)")
        else:
            print()
    
    # Write output
    outpath = OUTPUTS_DIR / "tripwires.csv"
    fields = ["company", "id", "trigger", "metric", "threshold", "action", 
              "observable", "status", "current_distance_pct", "as_of_date"]
    with open(outpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(distances)
    print(f"\n-> Wrote {outpath}")
    
    # Provenance
    provenance_rows = []
    for d in distances:
        provenance_rows.append({
            "timestamp": "2026-10-27", "company": d["company"],
            "metric": f"tripwire_{d['id']}", "fy": "ongoing",
            "value": d["status"],
            "unit": "status",
            "source_file": "tripwires.py",
            "notes": f"Phase 9: {d['trigger'][:60]}",
        })
    
    with open(PROVENANCE_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "company", "metric", "fy", "value", "unit", "source_file", "notes"])
        writer.writerows(provenance_rows)
    
    print(f"-> Appended {len(provenance_rows)} provenance entries")
    print("\n" + "=" * 60)
    print("PHASE 9 COMPLETE")
    print("=" * 60)
    return distances


if __name__ == "__main__":
    main()
