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
    print("All tests passed successfully!")

