import os
import sys
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from config import CUTOFF_DATE, assert_before_cutoff, MANDATE_CAPITAL_INR, COMPANIES

def test_cutoff_date():
    """Assert CUTOFF_DATE rule is strictly 2026-10-26."""
    assert str(CUTOFF_DATE) == "2026-10-26"
    assert_before_cutoff("2026-10-26", "Test cutoff exact")
    try:
        assert_before_cutoff("2026-10-27", "Test cutoff violation")
        assert False, "Should raise AssertionError on future date"
    except AssertionError:
        pass

def test_provenance_integrity():
    """Check provenance ledger exists and has entries."""
    provenance_path = ROOT / "data" / "provenance.csv"
    assert provenance_path.exists(), "provenance.csv must exist"
    with open(provenance_path, mode="r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) > 100, f"Expected >100 provenance entries, got {len(reader)}"

def test_outputs_exist():
    """Check that all required pipeline output files exist."""
    required_outputs = [
        "market_data.csv",
        "driver_models.csv",
        "forecasts.csv",
        "dcf_results.csv",
        "relative_valuation.csv",
        "scenarios.csv",
        "montecarlo_stats.csv",
        "robust_pick.json",
        "forensic_scores.csv",
        "sizing.csv",
        "tripwires.csv",
        "warroom_debate.csv",
        "verification_report.csv",
        "valuation.xlsx"
    ]
    for out in required_outputs:
        fpath = ROOT / "outputs" / out
        assert fpath.exists(), f"Output file missing: {out}"

def test_memo_exists():
    """Check that institutional IC investment memo exists."""
    memo_pdf = ROOT / "memo" / "ic_memo.pdf"
    assert memo_pdf.exists(), "ic_memo.pdf must exist in memo/"
    assert memo_pdf.stat().st_size > 1000, "ic_memo.pdf should not be empty"

def test_sizing_constraints():
    """Check that capital allocation sums to mandate and respects constraints."""
    sizing_path = ROOT / "outputs" / "sizing.csv"
    assert sizing_path.exists()
    with open(sizing_path, mode="r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    total_alloc_cr = sum(float(r["allocation_crore"]) for r in rows)
    # Total portfolio should be within mandate (500 Cr, remaining held as cash)
    assert total_alloc_cr <= 500.0 * 1.001
    assert total_alloc_cr >= 300.0  # reasonable invested capital
    for r in rows:
        assert r["ownership_ok"] == "YES", f"Ownership breached for {r['company']}"
        assert r["ff_ok"] == "YES", f"Free-float ownership breached for {r['company']}"

def test_valuation_reconciliation():
    """Verify that market caps and P/E reconcile with shares outstanding and audited prices."""
    mkt_path = ROOT / "outputs" / "market_data.csv"
    assert mkt_path.exists()
    with open(mkt_path, mode="r", encoding="utf-8") as f:
        mkt = {r["company"]: r for r in csv.DictReader(f)}
    
    rel_path = ROOT / "outputs" / "relative_valuation.csv"
    assert rel_path.exists()
    with open(rel_path, mode="r", encoding="utf-8") as f:
        rel = {r["company"]: r for r in csv.DictReader(f)}

    for co in ["BSE", "CDSL", "CAMS", "KFIN"]:
        p = float(mkt[co]["latest_price"])
        sh = int(float(mkt[co]["shares_outstanding"]))
        mcap = float(mkt[co]["market_cap_crore"])
        calc_mcap = round(p * sh / 1e7, 2)
        assert abs(mcap - calc_mcap) < 1.0, f"MCap mismatch for {co}: {mcap} vs {calc_mcap}"
        
        # P/E reconciles to price / eps
        eps = float(rel[co]["eps"])
        pe = float(rel[co]["pe"])
        calc_pe = round(p / eps, 1)
        assert abs(pe - calc_pe) < 0.2, f"P/E mismatch for {co}: {pe} vs {calc_pe}"
        # Assert sensible institutional ranges (no 1.5x P/E for BSE)
        assert pe > 15.0, f"Unrealistically low P/E for {co}: {pe}"

def test_dcf_and_simulation_sanity():
    """Ensure DCF bridges and Monte Carlo distributions are economically defensible and finite."""
    mc_path = ROOT / "outputs" / "montecarlo_stats.csv"
    assert mc_path.exists()
    with open(mc_path, mode="r", encoding="utf-8") as f:
        mc = {r["company"]: r for r in csv.DictReader(f)}
    
    for co in ["BSE", "CDSL", "CAMS", "KFIN"]:
        curr = float(mc[co]["current_price"])
        mean_p = float(mc[co]["mean_price"])
        p5 = float(mc[co]["p5"])
        p95 = float(mc[co]["p95"])
        exp_ret = float(mc[co]["expected_return_pct"])
        
        # Finite and positive
        assert p5 > 0 and mean_p > 0 and p95 > p5
        # Expected return must NOT be absurdly high (e.g. not 82,166%)
        assert -100.0 <= exp_ret <= 100.0, f"Outlandish expected return for {co}: {exp_ret}%"
        # Median simulated price must be reasonable relative to current price
        assert mean_p < curr * 3.0, f"Simulated price explosion for {co}: {mean_p} vs {curr}"

def test_final_deliverables_exist():
    """Verify final submission PDF and markdown report artifacts exist with content."""
    report_pdf = ROOT / "final_deliverables" / "Zeckathon_Final_Research_Report.pdf"
    assert report_pdf.exists(), "Final Research Report PDF missing"
    assert report_pdf.stat().st_size > 5000, "Final Research Report PDF empty"
    
    memo_pdf = ROOT / "final_deliverables" / "Zeckathon_Investment_Committee_Memo.pdf"
    assert memo_pdf.exists(), "IC Memo PDF missing in final_deliverables/"
    assert memo_pdf.stat().st_size > 5000, "IC Memo PDF empty"

if __name__ == "__main__":
    print("Running pipeline verification test suite...")
    test_cutoff_date()
    print("  [PASS] test_cutoff_date")
    test_provenance_integrity()
    print("  [PASS] test_provenance_integrity")
    test_outputs_exist()
    print("  [PASS] test_outputs_exist")
    test_memo_exists()
    print("  [PASS] test_memo_exists")
    test_sizing_constraints()
    print("  [PASS] test_sizing_constraints")
    test_valuation_reconciliation()
    print("  [PASS] test_valuation_reconciliation")
    test_dcf_and_simulation_sanity()
    print("  [PASS] test_dcf_and_simulation_sanity")
    test_final_deliverables_exist()
    print("  [PASS] test_final_deliverables_exist")
    print("All tests passed successfully!")


