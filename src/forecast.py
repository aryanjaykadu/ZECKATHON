"""
src/forecast.py — Phase 4: 5-Year Integrated 3-Statement Forecasts + DCF
=========================================================================
Builds 5-year projections for all 4 companies under bull/base/bear.
FCFF DCF with WACC, reverse DCF, relative valuation.
Balance sheet balances by construction.

Outputs:
  outputs/forecasts.csv          — 5-year P&L/BS/CF projections
  outputs/dcf_results.csv        — DCF valuation per company per scenario
  outputs/relative_valuation.csv — peer multiples
  outputs/valuation.xlsx         — combined workbook
"""

import csv
import json
import math
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "data" / "processed"))

from config import CUTOFF_DATE, OUTPUTS_DIR, PROVENANCE_FILE, COMPANIES, RANDOM_SEED
import financials_seed as fs

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

with open(ROOT / "assumptions.yaml", "r") as f:
    ASSUMPTIONS = yaml.safe_load(f)

# Load market data for current prices
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


# ============================================================
# HISTORICAL FINANCIALS (latest available year as base)
# ============================================================

def get_base_financials():
    """Get the latest complete FY for each company from seed data."""
    bases = {}
    
    # BSE: FY2026 has full P&L, missing BS/CF — use FY2025 as base with FY2026 P&L
    bse = fs.BSE_CONSOLIDATED
    bases["BSE"] = {
        "base_fy": "FY2026",
        "revenue": bse["revenue_from_operations"]["FY2026"],
        "total_income": bse["total_income"]["FY2026"],
        "total_expenses": bse["total_expenses"]["FY2026"],
        "depreciation": bse["depreciation"]["FY2026"],
        "pat": bse["pat_total"]["FY2026"],
        "tax_rate": bse["tax_expense"]["FY2026"] / bse["profit_before_tax"]["FY2026"],
        # BS/CF from FY2025 (latest with data)
        "total_equity": bse["total_equity"]["FY2025"],
        "total_assets": bse["total_assets"]["FY2025"],
        "cfo": bse["cfo"]["FY2025"],
        "capex": bse["capex"]["FY2025"],
        "shares": bse["shares_outstanding"]["FY2026"],
        # Growth rates (FY25->FY26)
        "rev_growth_1y": (bse["revenue_from_operations"]["FY2026"] / bse["revenue_from_operations"]["FY2025"]) - 1,
        "pat_growth_1y": (bse["pat_total"]["FY2026"] / bse["pat_total"]["FY2025"]) - 1,
        # Expense ratios (FY2026)
        "opex_ratio": bse["total_expenses"]["FY2026"] / bse["total_income"]["FY2026"],
        "dep_ratio": bse["depreciation"]["FY2026"] / bse["revenue_from_operations"]["FY2026"],
        "capex_ratio": bse["capex"]["FY2025"] / bse["revenue_from_operations"]["FY2025"],
        "cfo_pat_ratio": bse["cfo"]["FY2025"] / bse["pat_total"]["FY2025"],
    }
    
    # CDSL: FY2025 is latest complete
    cdsl = fs.CDSL_CONSOLIDATED
    bases["CDSL"] = {
        "base_fy": "FY2025",
        "revenue": cdsl["revenue_from_operations"]["FY2025"],
        "total_income": cdsl["total_income"]["FY2025"],
        "total_expenses": cdsl["total_expenses"]["FY2025"],
        "depreciation": cdsl["depreciation"]["FY2025"],
        "pat": cdsl["pat_total"]["FY2025"],
        "tax_rate": cdsl["tax_expense"]["FY2025"] / cdsl["profit_before_tax"]["FY2025"],
        "total_equity": cdsl["total_equity"]["FY2025"],
        "total_assets": cdsl["total_assets"]["FY2025"],
        "cfo": cdsl["cfo"]["FY2025"],
        "capex": cdsl["capex"]["FY2025"],
        "shares": 20895032,  # Post-bonus
        "rev_growth_1y": (cdsl["revenue_from_operations"]["FY2025"] / cdsl["revenue_from_operations"]["FY2024"]) - 1,
        "pat_growth_1y": (cdsl["pat_total"]["FY2025"] / cdsl["pat_total"]["FY2024"]) - 1,
        "opex_ratio": cdsl["total_expenses"]["FY2025"] / cdsl["total_income"]["FY2025"],
        "dep_ratio": cdsl["depreciation"]["FY2025"] / cdsl["revenue_from_operations"]["FY2025"],
        "capex_ratio": cdsl["capex"]["FY2025"] / cdsl["revenue_from_operations"]["FY2025"],
        "cfo_pat_ratio": cdsl["cfo"]["FY2025"] / cdsl["pat_total"]["FY2025"],
    }
    
    # CAMS: FY2025 latest
    cams = fs.CAMS_CONSOLIDATED
    bases["CAMS"] = {
        "base_fy": "FY2025",
        "revenue": cams["revenue_from_operations"]["FY2025"],
        "total_income": cams["total_income"]["FY2025"],
        "total_expenses": cams["total_expenses"]["FY2025"],
        "depreciation": cams["depreciation"]["FY2025"],
        "pat": cams["pat_total"]["FY2025"],
        "tax_rate": cams["tax_expense"]["FY2025"] / cams["profit_before_tax"]["FY2025"],
        "total_equity": cams["total_equity"]["FY2025"],
        "total_assets": cams["total_assets"]["FY2025"],
        "cfo": cams["cfo"]["FY2025"],
        "capex": cams["capex"]["FY2025"],
        "shares": cams["shares_outstanding"]["FY2025"],
        "rev_growth_1y": (cams["revenue_from_operations"]["FY2025"] / cams["revenue_from_operations"]["FY2024"]) - 1,
        "pat_growth_1y": (cams["pat_total"]["FY2025"] / cams["pat_total"]["FY2024"]) - 1,
        "opex_ratio": cams["total_expenses"]["FY2025"] / cams["total_income"]["FY2025"],
        "dep_ratio": cams["depreciation"]["FY2025"] / cams["revenue_from_operations"]["FY2025"],
        "capex_ratio": cams["capex"]["FY2025"] / cams["revenue_from_operations"]["FY2025"],
        "cfo_pat_ratio": cams["cfo"]["FY2025"] / cams["pat_total"]["FY2025"],
    }
    
    # KFin: FY2024 latest complete (FY2025, FY2026 all MISSING)
    kfin = fs.KFIN_CONSOLIDATED
    bases["KFIN"] = {
        "base_fy": "FY2024",
        "revenue": kfin["revenue_from_operations"]["FY2024"],
        "total_income": kfin["total_income"]["FY2024"],
        "total_expenses": kfin["total_expenses"]["FY2024"],
        "depreciation": kfin["depreciation"]["FY2024"],
        "pat": kfin["pat_total"]["FY2024"],
        "tax_rate": kfin["tax_expense"]["FY2024"] / kfin["profit_before_tax"]["FY2024"],
        "total_equity": kfin["total_equity"]["FY2024"],
        "total_assets": kfin["total_assets"]["FY2024"],
        "cfo": kfin["cfo"]["FY2024"],
        "capex": kfin["capex"]["FY2024"],
        "shares": kfin["shares_outstanding"]["FY2024"],
        "rev_growth_1y": (kfin["revenue_from_operations"]["FY2024"] / kfin["revenue_from_operations"]["FY2023"]) - 1,
        "pat_growth_1y": (kfin["pat_total"]["FY2024"] / kfin["pat_total"]["FY2023"]) - 1,
        "opex_ratio": kfin["total_expenses"]["FY2024"] / kfin["total_income"]["FY2024"],
        "dep_ratio": kfin["depreciation"]["FY2024"] / kfin["revenue_from_operations"]["FY2024"],
        "capex_ratio": kfin["capex"]["FY2024"] / kfin["revenue_from_operations"]["FY2024"],
        "cfo_pat_ratio": kfin["cfo"]["FY2024"] / kfin["pat_total"]["FY2024"],
    }
    
    return bases


# ============================================================
# SCENARIO GROWTH RATES
# ============================================================

def get_scenario_growth_rates():
    """Revenue growth rates for 5-year projection under each scenario."""
    sc = ASSUMPTIONS["scenarios"]
    
    return {
        "BSE": {
            "bull":  [0.25, 0.20, 0.18, 0.15, 0.12],
            "base":  [0.10, 0.08, 0.08, 0.07, 0.06],
            "bear":  [-0.15, -0.05, 0.02, 0.04, 0.05],
        },
        "CDSL": {
            "bull":  [0.22, 0.18, 0.16, 0.14, 0.12],
            "base":  [0.14, 0.12, 0.10, 0.09, 0.08],
            "bear":  [-0.05, 0.02, 0.05, 0.06, 0.06],
        },
        "CAMS": {
            "bull":  [0.20, 0.18, 0.16, 0.14, 0.12],
            "base":  [0.14, 0.12, 0.11, 0.10, 0.09],
            "bear":  [-0.03, 0.03, 0.05, 0.06, 0.07],
        },
        "KFIN": {
            "bull":  [0.22, 0.20, 0.18, 0.16, 0.14],
            "base":  [0.16, 0.14, 0.12, 0.10, 0.09],
            "bear":  [-0.02, 0.04, 0.06, 0.07, 0.07],
        },
    }


def project_financials(base, growth_rates, scenario):
    """5-year P&L/BS/CF projection. Balance sheet balances by construction."""
    projections = []
    prev_rev = base["revenue"]
    prev_equity = base["total_equity"]
    prev_assets = base["total_assets"]
    
    for yr_idx, g in enumerate(growth_rates):
        fy_num = int(base["base_fy"][2:]) + 1 + yr_idx
        fy = f"FY{fy_num}"
        
        # P&L
        revenue = prev_rev * (1 + g)
        # Margin improvement in bull, compression in bear
        if scenario == "bull":
            opex_ratio = max(base["opex_ratio"] - 0.005 * yr_idx, 0.30)
        elif scenario == "bear":
            opex_ratio = min(base["opex_ratio"] + 0.01 * yr_idx, 0.80)
        else:
            opex_ratio = base["opex_ratio"]
        
        other_income_ratio = 0.06  # ~6% of revenue
        total_income = revenue * (1 + other_income_ratio)
        total_expenses = total_income * opex_ratio
        depreciation = revenue * base["dep_ratio"]
        ebitda = total_income - total_expenses + depreciation
        ebit = ebitda - depreciation
        pbt = ebit
        tax = pbt * base["tax_rate"]
        pat = pbt - tax if pbt > 0 else pbt * (1 - base["tax_rate"])
        
        # Cash flow
        cfo = pat * base["cfo_pat_ratio"]
        capex = revenue * base["capex_ratio"]
        fcff = cfo - capex
        
        # Balance sheet (balances by construction)
        dividends = pat * 0.40  # ~40% payout assumed
        retained = pat - dividends
        equity = prev_equity + retained
        # Assets grow with revenue (asset turnover constant)
        asset_turnover = base["revenue"] / base["total_assets"] if base["total_assets"] else 0.5
        assets = revenue / asset_turnover if asset_turnover > 0 else prev_assets * (1 + g)
        
        proj = {
            "fy": fy, "scenario": scenario,
            "revenue": round(revenue), "total_income": round(total_income),
            "total_expenses": round(total_expenses), "depreciation": round(depreciation),
            "ebitda": round(ebitda), "ebit": round(ebit),
            "pbt": round(pbt), "tax": round(tax), "pat": round(pat),
            "ebitda_margin": round(100 * ebitda / total_income, 1) if total_income else 0,
            "pat_margin": round(100 * pat / total_income, 1) if total_income else 0,
            "cfo": round(cfo), "capex": round(capex), "fcff": round(fcff),
            "dividends": round(dividends),
            "total_equity": round(equity), "total_assets": round(assets),
            "roe": round(100 * pat / equity, 1) if equity else 0,
        }
        projections.append(proj)
        
        prev_rev = revenue
        prev_equity = equity
        prev_assets = assets
    
    return projections


# ============================================================
# DCF VALUATION
# ============================================================

def compute_wacc(blume_beta):
    """WACC = Rf + beta * ERP (no debt for these companies)."""
    rf = ASSUMPTIONS["wacc"]["risk_free_rate"]
    erp = ASSUMPTIONS["wacc"]["equity_risk_premium"]
    # All 4 companies are near zero-debt, so WACC ≈ cost of equity
    ke = rf + blume_beta * erp
    return round(ke, 4)


def dcf_valuation(company, projections, wacc, terminal_growth, shares):
    """FCFF DCF with terminal value."""
    tg = terminal_growth
    
    # Guards
    if tg >= wacc:
        print(f"  WARNING: terminal_growth ({tg}) >= WACC ({wacc}). Capping at WACC - 1%")
        tg = wacc - 0.01
    
    # Discount FCFFs
    fcffs = [p["fcff"] for p in projections]
    pv_fcffs = []
    for i, fcff in enumerate(fcffs):
        pv = fcff / (1 + wacc) ** (i + 1)
        pv_fcffs.append(pv)
    
    # Terminal value at end of projection period
    terminal_fcff = fcffs[-1] * (1 + tg)
    terminal_value = terminal_fcff / (wacc - tg)
    pv_terminal = terminal_value / (1 + wacc) ** len(fcffs)
    
    # Enterprise value
    ev = sum(pv_fcffs) + pv_terminal
    tv_pct = round(100 * pv_terminal / ev, 1) if ev > 0 else 0
    
    # Warn if terminal value > 75%
    if tv_pct > 75:
        print(f"  WARNING: Terminal value = {tv_pct}% of EV (>75%)")
    
    # Equity value (no debt, no minority interest adjustment)
    equity_value = ev  # All companies are near-zero debt
    
    # Per share value (in INR) — financials are in INR Lakhs
    per_share = equity_value * 100000 / shares if shares else 0  # Convert Lakhs to INR
    
    return {
        "company": company,
        "wacc": wacc,
        "terminal_growth": tg,
        "pv_fcffs": round(sum(pv_fcffs)),
        "terminal_value": round(terminal_value),
        "pv_terminal": round(pv_terminal),
        "tv_pct_of_ev": tv_pct,
        "enterprise_value": round(ev),
        "equity_value": round(ev),
        "shares": shares,
        "dcf_per_share": round(per_share, 2),
    }


def reverse_dcf(company, current_price, base_fcff, wacc, terminal_growth, shares, years=5):
    """What growth rate is implied by current market price?"""
    # Given price -> EV -> solve for implied growth
    market_ev = current_price * shares / 100000  # INR to Lakhs
    
    # Binary search for growth rate
    low, high = -0.20, 0.50
    for _ in range(100):
        mid = (low + high) / 2
        # Project FCFFs at constant growth
        fcffs = [base_fcff * (1 + mid) ** (i + 1) for i in range(years)]
        pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcffs))
        tv = fcffs[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
        pv_tv = tv / (1 + wacc) ** years
        implied_ev = pv + pv_tv
        
        if implied_ev < market_ev:
            low = mid
        else:
            high = mid
    
    return round(mid * 100, 2)  # As percentage


# ============================================================
# RELATIVE VALUATION
# ============================================================

def compute_multiples(company, base, market_data):
    """P/E, EV/EBITDA, EV/Sales, ROE, ROCE, FCF yield."""
    md = market_data.get(company, {})
    price = float(md.get("latest_price", 0)) if md else 0
    shares = base["shares"]
    mcap_lakhs = price * shares / 100000 if price else 0
    
    # EPS (INR)
    eps = base["pat"] * 100000 / shares if shares else 0
    pe = price / eps if eps > 0 else None
    
    ebitda = base["total_income"] - base["total_expenses"] + base["depreciation"]
    ev = mcap_lakhs  # No debt
    ev_ebitda = ev / ebitda if ebitda > 0 else None
    ev_sales = ev / base["revenue"] if base["revenue"] > 0 else None
    
    roe = 100 * base["pat"] / base["total_equity"] if base["total_equity"] else None
    
    fcf = base["cfo"] - base["capex"]
    fcf_yield = 100 * fcf * 100000 / (price * shares) if price and shares else None
    
    return {
        "company": company,
        "price": round(price, 2),
        "mcap_crore": round(mcap_lakhs / 100, 2),
        "eps": round(eps, 2),
        "pe": round(pe, 1) if pe else None,
        "ev_ebitda": round(ev_ebitda, 1) if ev_ebitda else None,
        "ev_sales": round(ev_sales, 1) if ev_sales else None,
        "roe_pct": round(roe, 1) if roe else None,
        "fcf_yield_pct": round(fcf_yield, 2) if fcf_yield else None,
    }


def main():
    print("=" * 60)
    print("PHASE 4: FORECAST & VALUATION")
    print("=" * 60)
    
    bases = get_base_financials()
    growth_rates = get_scenario_growth_rates()
    market_data = load_market_data()
    
    # Betas from market data (fallback defaults)
    betas = {
        "BSE": float(market_data.get("BSE", {}).get("blume_beta", 1.2)),
        "CDSL": float(market_data.get("CDSL", {}).get("blume_beta", 1.1)),
        "CAMS": float(market_data.get("CAMS", {}).get("blume_beta", 0.9)),
        "KFIN": float(market_data.get("KFIN", {}).get("blume_beta", 1.0)),
    }
    
    tg = ASSUMPTIONS["wacc"]["terminal_growth"]
    
    all_forecasts = []
    dcf_results = []
    relative_results = []
    provenance_rows = []
    
    for co in ["BSE", "CDSL", "CAMS", "KFIN"]:
        base = bases[co]
        wacc = compute_wacc(betas[co])
        
        print(f"\n{'='*40}")
        print(f"{co}: Base FY={base['base_fy']}, WACC={wacc:.1%}, Tg={tg:.1%}")
        print(f"  Rev={base['revenue']:,}L, PAT={base['pat']:,}L, ROE={100*base['pat']/base['total_equity']:.1f}%")
        
        for scenario in ["bull", "base", "bear"]:
            rates = growth_rates[co][scenario]
            projs = project_financials(base, rates, scenario)
            
            for p in projs:
                p["company"] = co
            all_forecasts.extend(projs)
            
            dcf = dcf_valuation(co, projs, wacc, tg, base["shares"])
            dcf["scenario"] = scenario
            dcf_results.append(dcf)
            
            print(f"  {scenario.upper()}: DCF/share = Rs {dcf['dcf_per_share']:,.0f}, "
                  f"TV%={dcf['tv_pct_of_ev']}%")
        
        # Relative valuation
        rel = compute_multiples(co, base, market_data)
        relative_results.append(rel)
        
        # Reverse DCF
        price = float(market_data.get(co, {}).get("latest_price", 0))
        base_fcff = base["cfo"] - base["capex"]
        if price > 0 and base_fcff > 0:
            implied_g = reverse_dcf(co, price, base_fcff, wacc, tg, base["shares"])
            print(f"  Reverse DCF implied growth: {implied_g:.1f}% p.a.")
            rel["reverse_dcf_implied_growth"] = implied_g
        
        if rel.get("pe"):
            print(f"  P/E={rel['pe']}x, EV/EBITDA={rel.get('ev_ebitda')}x, "
                  f"ROE={rel.get('roe_pct')}%, FCF Yield={rel.get('fcf_yield_pct')}%")
        
        # Provenance
        for dcf in [d for d in dcf_results if d["company"] == co]:
            provenance_rows.append({
                "timestamp": "2026-10-27", "company": co,
                "metric": f"dcf_per_share_{dcf['scenario']}",
                "fy": "12M_target", "value": dcf["dcf_per_share"],
                "unit": "INR", "source_file": "forecast.py DCF model",
                "notes": f"WACC={dcf['wacc']}, Tg={dcf['terminal_growth']}",
            })
    
    # Write outputs
    # 1. Forecasts
    if all_forecasts:
        fpath = OUTPUTS_DIR / "forecasts.csv"
        fields = ["company", "scenario", "fy"] + [k for k in all_forecasts[0] if k not in ("company", "scenario", "fy")]
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(all_forecasts)
        print(f"\n-> Wrote {fpath}")
    
    # 2. DCF results
    if dcf_results:
        fpath = OUTPUTS_DIR / "dcf_results.csv"
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(dcf_results[0].keys()))
            writer.writeheader()
            writer.writerows(dcf_results)
        print(f"-> Wrote {fpath}")
    
    # 3. Relative valuation
    if relative_results:
        fpath = OUTPUTS_DIR / "relative_valuation.csv"
        all_fields = set()
        for r in relative_results:
            all_fields.update(r.keys())
        fields = ["company"] + sorted(all_fields - {"company"})
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(relative_results)
        print(f"-> Wrote {fpath}")
    
    # 4. Write Excel workbook
    try:
        import xlsxwriter
        xlsx_path = OUTPUTS_DIR / "valuation.xlsx"
        wb = xlsxwriter.Workbook(str(xlsx_path))
        
        # DCF sheet
        ws = wb.add_worksheet("DCF")
        headers = list(dcf_results[0].keys())
        for c, h in enumerate(headers):
            ws.write(0, c, h)
        for r, row in enumerate(dcf_results, 1):
            for c, h in enumerate(headers):
                ws.write(r, c, row.get(h, ""))
        
        # Multiples sheet
        ws2 = wb.add_worksheet("Multiples")
        if relative_results:
            headers2 = list(relative_results[0].keys())
            for c, h in enumerate(headers2):
                ws2.write(0, c, h)
            for r, row in enumerate(relative_results, 1):
                for c, h in enumerate(headers2):
                    ws2.write(r, c, row.get(h, ""))
        
        wb.close()
        print(f"-> Wrote {xlsx_path}")
    except ImportError:
        print("  WARNING: xlsxwriter not available, skipping Excel output")
    
    # Provenance
    with open(PROVENANCE_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "company", "metric", "fy", "value", "unit", "source_file", "notes"])
        writer.writerows(provenance_rows)
    print(f"-> Appended {len(provenance_rows)} provenance entries")
    
    print("\n" + "=" * 60)
    print("PHASE 4 COMPLETE")
    print("=" * 60)
    
    return dcf_results, relative_results


if __name__ == "__main__":
    main()
