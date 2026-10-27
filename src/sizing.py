"""
src/sizing.py — Phase 8: Liquidity & Sizing
=============================================
Rs 500 Cr allocation execution plan.
ADV participation (10/15/20%), impact cost, ownership thresholds.

Outputs:
  outputs/sizing.csv — allocation and execution plan
"""

import csv
import json
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "data" / "processed"))

from config import OUTPUTS_DIR, PROVENANCE_FILE, MANDATE_CAPITAL_INR

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

with open(ROOT / "assumptions.yaml", "r") as f:
    ASSUMPTIONS = yaml.safe_load(f)


def load_market_data():
    """Load market data CSV."""
    mkt = {}
    mpath = OUTPUTS_DIR / "market_data.csv"
    if not mpath.exists():
        return mkt
    with open(mpath, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mkt[row["company"]] = row
    return mkt


def load_robust_pick():
    """Load robust pick results."""
    ppath = OUTPUTS_DIR / "robust_pick.json"
    if not ppath.exists():
        return None
    with open(ppath, "r") as f:
        return json.load(f)


def main():
    print("=" * 60)
    print("PHASE 8: LIQUIDITY & SIZING")
    print("=" * 60)
    
    mkt = load_market_data()
    pick = load_robust_pick()
    sizing = ASSUMPTIONS["sizing"]
    mandate = MANDATE_CAPITAL_INR  # Rs 500 Cr in paisa-free INR
    mandate_crore = mandate / 1e7  # 500 Cr
    
    print(f"\nMandate: Rs {mandate_crore:.0f} Crore")
    print(f"ADV participation levels: {sizing['adv_participation_pct']}%")
    print(f"Max ownership: {sizing['max_ownership_pct']}%")
    print(f"Max free-float: {sizing['max_free_float_pct']}%")
    
    results = []
    
    # Allocation based on robust pick
    if pick:
        win_shares = pick.get("win_shares", {})
        fragile = pick.get("fragile", True)
        
        if fragile:
            # Split allocation based on win shares
            total_wins = sum(win_shares.values())
            allocations = {co: round(ws / total_wins * 100, 1) 
                          for co, ws in win_shares.items()}
        else:
            # Concentrated in winner, diversified rest
            winner = pick["pick"]
            allocations = {}
            for co in win_shares:
                if co == winner:
                    allocations[co] = 60.0  # 60% to winner
                else:
                    allocations[co] = round(40.0 / (len(win_shares) - 1), 1)
    else:
        # Equal weight fallback
        allocations = {"BSE": 25.0, "CDSL": 25.0, "CAMS": 25.0, "KFIN": 25.0}
    
    # Ownership constraint pass: cap each position at max_ownership_pct (iterative)
    max_own = sizing["max_ownership_pct"] / 100  # 4.9% -> 0.049
    max_ff = sizing["max_free_float_pct"] / 100  # 10% -> 0.10
    
    # Compute per-company max allocation (INR) based on ownership + free-float limits
    max_alloc_pct_map = {}
    for co in list(allocations.keys()):
        md = mkt.get(co, {})
        price = float(md.get("latest_price", 0) or 0)
        shares = int(float(md.get("shares_outstanding", 0) or 0))
        ff_pct = float(md.get("free_float_pct", 75) or 75) / 100
        if price > 0 and shares > 0:
            # Limit by total ownership (use 0.98 safety margin to avoid floating point/rounding breach)
            max_by_own = max_own * 0.98 * shares * price
            # Limit by free-float ownership
            max_by_ff = max_ff * 0.98 * shares * ff_pct * price
            max_alloc_inr = min(max_by_own, max_by_ff)
            max_alloc_pct_map[co] = max_alloc_inr / (mandate_crore * 1e7) * 100
        else:
            max_alloc_pct_map[co] = 100.0  # No constraint if no data
    
    # Iteratively cap and redistribute (max 10 iterations)
    for iteration in range(10):
        any_capped = False
        for co in list(allocations.keys()):
            cap = max_alloc_pct_map.get(co, 100)
            if allocations[co] > cap:
                print(f"  Ownership cap: {co} capped from {allocations[co]:.1f}% to {cap:.1f}%")
                allocations[co] = round(cap, 1)
                any_capped = True
        
        total_alloc = sum(allocations.values())
        if total_alloc < 99.9:
            shortfall = 100 - total_alloc
            uncapped = [co for co in allocations 
                       if allocations[co] < max_alloc_pct_map.get(co, 100) - 0.1]
            if uncapped:
                per_co = shortfall / len(uncapped)
                for co in uncapped:
                    allocations[co] = round(allocations[co] + per_co, 1)
            else:
                # All positions at cap — hold remainder as cash
                print(f"  All positions at ownership cap. Unallocated: {100 - total_alloc:.1f}% (cash)")
                break
        
        if not any_capped:
            break
    
    print(f"\nAllocation weights (ownership-constrained): {allocations}")
    
    for co in ["BSE", "CDSL", "CAMS", "KFIN"]:
        md = mkt.get(co, {})
        price = float(md.get("latest_price", 0) or 0)
        adtv_crore = float(md.get("adtv_30d_crore", 0) or 0)
        adv = float(md.get("adv_30d", 0) or 0)
        ff_mcap = float(md.get("free_float_mcap_crore", 0) or 0)
        shares = int(float(md.get("shares_outstanding", 0) or 0))
        ff_pct = float(md.get("free_float_pct", 75) or 75)
        
        alloc_pct = allocations.get(co, 0)
        alloc_crore = mandate_crore * alloc_pct / 100
        alloc_inr = alloc_crore * 1e7
        
        # Shares to buy
        shares_to_buy = int(alloc_inr / price) if price > 0 else 0
        
        # Ownership check
        ownership_pct = (shares_to_buy / shares * 100) if shares > 0 else 0
        ownership_ok = ownership_pct < sizing["max_ownership_pct"]
        
        # Free float check
        ff_shares = int(shares * ff_pct / 100)
        ff_ownership_pct = (shares_to_buy / ff_shares * 100) if ff_shares > 0 else 0
        ff_ok = ff_ownership_pct < sizing["max_free_float_pct"]
        
        # Execution days at various participation rates
        exec_days = {}
        for part_pct in sizing["adv_participation_pct"]:
            daily_volume = adv * (part_pct / 100) if adv > 0 else 0
            days = int(shares_to_buy / daily_volume) + 1 if daily_volume > 0 else 999
            exec_days[f"{part_pct}pct"] = days
        
        # Impact cost estimate (simplified: 0.1% per day of ADTV)
        days_at_15 = exec_days.get("15pct", 10)
        impact_cost_bps = round(10 * days_at_15, 0)  # ~10 bps per day
        impact_cost_bps = min(impact_cost_bps, 200)  # Cap at 200 bps
        
        row = {
            "company": co,
            "allocation_pct": alloc_pct,
            "allocation_crore": round(alloc_crore, 2),
            "current_price": price,
            "shares_to_buy": shares_to_buy,
            "ownership_pct": round(ownership_pct, 2),
            "ownership_ok": "YES" if ownership_ok else "BREACH",
            "ff_ownership_pct": round(ff_ownership_pct, 2),
            "ff_ok": "YES" if ff_ok else "BREACH",
            "adtv_crore": adtv_crore,
            "exec_days_10pct_adv": exec_days.get("10pct", 999),
            "exec_days_15pct_adv": exec_days.get("15pct", 999),
            "exec_days_20pct_adv": exec_days.get("20pct", 999),
            "impact_cost_bps": impact_cost_bps,
        }
        results.append(row)
        
        print(f"\n{co}:")
        print(f"  Allocation: {alloc_pct}% = Rs {alloc_crore:.1f} Cr")
        print(f"  Shares to buy: {shares_to_buy:,} ({ownership_pct:.2f}% ownership)")
        print(f"  Ownership check: {'PASS' if ownership_ok else 'BREACH'} (<{sizing['max_ownership_pct']}%)")
        print(f"  FF ownership: {ff_ownership_pct:.2f}% ({'PASS' if ff_ok else 'BREACH'})")
        print(f"  Execution days @10/15/20% ADV: {exec_days.get('10pct')}/{exec_days.get('15pct')}/{exec_days.get('20pct')}")
        print(f"  Est. impact cost: {impact_cost_bps:.0f} bps")
    
    # Write output
    outpath = OUTPUTS_DIR / "sizing.csv"
    if results:
        with open(outpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)
        print(f"\n-> Wrote {outpath}")
    
    # Provenance
    provenance_rows = []
    for r in results:
        for k, v in r.items():
            if k != "company":
                provenance_rows.append({
                    "timestamp": "2026-10-27", "company": r["company"],
                    "metric": f"sizing_{k}", "fy": "execution_plan",
                    "value": v, "unit": "various",
                    "source_file": "sizing.py + market_data.csv + assumptions.yaml",
                    "notes": "Phase 8 sizing",
                })
    
    with open(PROVENANCE_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "company", "metric", "fy", "value", "unit", "source_file", "notes"])
        writer.writerows(provenance_rows)
    
    print(f"-> Appended {len(provenance_rows)} provenance entries")
    print("\n" + "=" * 60)
    print("PHASE 8 COMPLETE")
    print("=" * 60)
    return results


if __name__ == "__main__":
    main()
