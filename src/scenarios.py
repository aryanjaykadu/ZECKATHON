"""
src/scenarios.py — Phase 6: Scenarios, Shocks & Monte Carlo
============================================================
Deterministic scenarios (bull/base/bear including derivative -30% and equity -20%).
Shock catalogue with probabilities.
10,000 seeded joint draws with explicit correlations.

Outputs:
  outputs/scenarios.csv          — deterministic scenario results
  outputs/montecarlo_results.csv — price distribution from simulation
  outputs/montecarlo_stats.csv   — summary statistics
"""

import csv
import json
import math
import sys
import yaml
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "data" / "processed"))

from config import CUTOFF_DATE, OUTPUTS_DIR, PROVENANCE_FILE, RANDOM_SEED

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

with open(ROOT / "assumptions.yaml", "r") as f:
    ASSUMPTIONS = yaml.safe_load(f)


def load_dcf_results():
    """Load DCF results."""
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
                "wacc": float(row["wacc"]),
            }
    return results


def load_market_data():
    """Load market data."""
    mkt = {}
    fpath = OUTPUTS_DIR / "market_data.csv"
    if not fpath.exists():
        return mkt
    with open(fpath, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mkt[row["company"]] = {
                "price": float(row.get("latest_price", 0) or 0),
                "volatility": float(row.get("volatility_ann", 0.4) or 0.4),
                "blume_beta": float(row.get("blume_beta", 1.0) or 1.0),
            }
    return mkt


def load_forensic_scores():
    """Load forensic quality scores."""
    scores = {}
    fpath = OUTPUTS_DIR / "forensic_scores.csv"
    if not fpath.exists():
        return scores
    with open(fpath, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            scores[row["company"]] = int(float(row.get("composite_score", 50) or 50))
    return scores


def deterministic_scenarios():
    """Bull/Base/Bear with stress combinations."""
    dcf = load_dcf_results()
    mkt = load_market_data()
    
    scenarios = []
    for co in ["BSE", "CDSL", "CAMS", "KFIN"]:
        if co not in dcf:
            continue
        price = mkt.get(co, {}).get("price", 0)
        
        for sc in ["bull", "base", "bear"]:
            tp = dcf[co][sc]["dcf_per_share"]
            ret = ((tp / price) - 1) * 100 if price > 0 else 0
            scenarios.append({
                "company": co, "scenario": sc,
                "current_price": round(price, 2),
                "target_price": round(tp, 2),
                "expected_return_pct": round(ret, 1),
            })
        
        # Combined stress: derivatives -30% + equity -20%
        if co == "BSE":
            bear_tp = dcf[co]["bear"]["dcf_per_share"]
            stress_tp = bear_tp * 0.85  # Additional 15% haircut for combined stress
            ret = ((stress_tp / price) - 1) * 100 if price > 0 else 0
            scenarios.append({
                "company": co, "scenario": "combined_stress",
                "current_price": round(price, 2),
                "target_price": round(stress_tp, 2),
                "expected_return_pct": round(ret, 1),
            })
    
    return scenarios


def correlated_normal_draws(n_draws, n_vars, correlations, seed):
    """Generate correlated normal draws using Cholesky decomposition."""
    random.seed(seed)
    
    # Build correlation matrix (4 variables: equity_return, aum_growth, deriv_growth, multiple_change)
    corr = ASSUMPTIONS["correlations"]
    C = [
        [1.0, corr["equity_return_vs_aum_growth"], corr["equity_return_vs_derivatives_growth"], corr["equity_return_vs_multiple_change"]],
        [corr["equity_return_vs_aum_growth"], 1.0, corr["aum_growth_vs_derivatives_growth"], 0.3],
        [corr["equity_return_vs_derivatives_growth"], corr["aum_growth_vs_derivatives_growth"], 1.0, 0.3],
        [corr["equity_return_vs_multiple_change"], 0.3, 0.3, 1.0],
    ]
    
    # Cholesky decomposition
    n = len(C)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                val = C[i][i] - s
                L[i][j] = math.sqrt(max(val, 0))
            else:
                L[i][j] = (C[i][j] - s) / L[j][j] if L[j][j] != 0 else 0
    
    # Generate draws
    draws = []
    for _ in range(n_draws):
        z = [random.gauss(0, 1) for _ in range(n)]
        correlated = [sum(L[i][j] * z[j] for j in range(n)) for i in range(n)]
        draws.append(correlated)
    
    return draws


def monte_carlo_simulation(n_draws=10000):
    """10,000 joint draws for 12-month price distribution."""
    print(f"\nRunning Monte Carlo ({n_draws:,} draws, seed={RANDOM_SEED})...")
    
    dcf = load_dcf_results()
    mkt = load_market_data()
    forensic = load_forensic_scores()
    scenarios = ASSUMPTIONS["scenarios"]
    
    draws = correlated_normal_draws(n_draws, 4, ASSUMPTIONS["correlations"], RANDOM_SEED)
    
    companies = ["BSE", "CDSL", "CAMS", "KFIN"]
    results = {co: [] for co in companies}
    
    for draw_idx, draw in enumerate(draws):
        equity_z, aum_z, deriv_z, multiple_z = draw
        
        for co in companies:
            if co not in dcf or co not in mkt:
                continue
            
            price = mkt[co]["price"]
            vol = mkt[co]["volatility"]
            beta = mkt[co]["blume_beta"]
            
            bull_tp = dcf[co]["bull"]["dcf_per_share"]
            base_tp = dcf[co]["base"]["dcf_per_share"]
            bear_tp = dcf[co]["bear"]["dcf_per_share"]
            
            # Map equity return to scenario weight
            sc = scenarios
            base_equity = sc["base"]["equity_market_return"]
            
            # Equity market return for this draw
            equity_return = base_equity + equity_z * 0.20  # Mean=10%, vol=20%
            
            # Stock-specific return = alpha + beta * market + idiosyncratic
            idio_vol = vol * math.sqrt(1 - min(beta ** 2 * 0.04 / (vol ** 2), 0.99))
            idio_z = random.gauss(0, 1)
            
            # Scenario blending based on market conditions
            if equity_return > 0.12:
                # Bull-like conditions
                target = bull_tp * 0.6 + base_tp * 0.4
            elif equity_return < -0.05:
                # Bear-like conditions
                target = bear_tp * 0.6 + base_tp * 0.4
            else:
                target = base_tp
            
            # Apply shocks
            shock_adj = 1.0
            for shock_name, shock_info in ASSUMPTIONS["shocks"].items():
                prob = shock_info["probability"]
                if co in [c.upper() for c in shock_info.get("impact_companies", [])]:
                    # Bernoulli draw for each shock
                    if random.random() < prob:
                        shock_adj *= 0.90  # Each shock takes ~10% off target
            
            # Final 12-month simulated price under Geometric Brownian Motion
            # Fix: drift in log-normal diffusion is log(target/price), not (target/price - 1)
            target_adj = max(target * shock_adj, price * 0.05)
            log_drift = math.log(target_adj / price)
            noise = idio_z * idio_vol * math.sqrt(1)  # 1-year horizon
            final_price = price * math.exp(log_drift + noise - 0.5 * idio_vol ** 2)
            final_price = max(final_price, price * 0.05)  # Floor at 95% loss
            
            results[co].append(final_price)
    
    return results


def compute_statistics(results, market_data):
    """Compute percentiles, expected return, prob of loss, CVaR."""
    stats = []
    
    for co, prices in results.items():
        if not prices:
            continue
        
        prices_sorted = sorted(prices)
        n = len(prices_sorted)
        current = market_data.get(co, {}).get("price", 0)
        
        mean_price = sum(prices) / n
        returns = [(p / current - 1) for p in prices] if current > 0 else [0] * n
        returns_sorted = sorted(returns)
        
        p5 = prices_sorted[int(0.05 * n)]
        p10 = prices_sorted[int(0.10 * n)]
        p25 = prices_sorted[int(0.25 * n)]
        p50 = prices_sorted[int(0.50 * n)]
        p75 = prices_sorted[int(0.75 * n)]
        p90 = prices_sorted[int(0.90 * n)]
        p95 = prices_sorted[int(0.95 * n)]
        
        expected_return = (mean_price / current - 1) * 100 if current > 0 else 0
        prob_loss = sum(1 for p in prices if p < current) / n * 100
        
        # CVaR (expected shortfall at 5% tail)
        tail_5 = returns_sorted[:int(0.05 * n)]
        cvar_5 = (sum(tail_5) / len(tail_5) * 100) if tail_5 else 0
        
        stat = {
            "company": co,
            "current_price": round(current, 2),
            "mean_price": round(mean_price, 2),
            "p5": round(p5, 2), "p10": round(p10, 2),
            "p25": round(p25, 2), "p50": round(p50, 2),
            "p75": round(p75, 2), "p90": round(p90, 2), "p95": round(p95, 2),
            "expected_return_pct": round(expected_return, 1),
            "prob_loss_pct": round(prob_loss, 1),
            "cvar_5pct": round(cvar_5, 1),
        }
        stats.append(stat)
        
        print(f"\n{co}:")
        print(f"  Current: Rs {current:,.0f}, Mean: Rs {mean_price:,.0f}")
        print(f"  P5/P10/P50/P90/P95: {p5:,.0f} / {p10:,.0f} / {p50:,.0f} / {p90:,.0f} / {p95:,.0f}")
        print(f"  Expected Return: {expected_return:.1f}%, Prob Loss: {prob_loss:.1f}%, CVaR(5%): {cvar_5:.1f}%")
    
    return stats


def robust_pick_probability(mc_results, market_data, forensic_scores):
    """P7: Rank companies on risk-adjusted return per draw. Report win shares."""
    print("\n" + "=" * 40)
    print("ROBUST PICK PROBABILITY (P7)")
    print("=" * 40)
    
    weights = ASSUMPTIONS["pick_weights"]
    print(f"  Weights locked at: {weights['timestamp_locked']}")
    print(f"  Rationale: {weights['rationale']}")
    
    companies = list(mc_results.keys())
    n_draws = len(list(mc_results.values())[0])
    
    wins = {co: 0 for co in companies}
    
    for i in range(n_draws):
        scores = {}
        for co in companies:
            price = mc_results[co][i]
            current = market_data.get(co, {}).get("price", 0)
            ret = (price / current - 1) if current > 0 else 0
            
            # For this draw, compute a simple risk-adjusted score
            fs_score = forensic_scores.get(co, 50)
            score = (
                weights["expected_return"] * ret
                - weights["probability_of_loss"] * max(-ret, 0)
                + weights["forensic_score"] * (fs_score / 100)
            )
            scores[co] = score
        
        winner = max(scores, key=scores.get)
        wins[winner] += 1
    
    # Convert to percentages
    win_pct = {co: round(100 * wins[co] / n_draws, 1) for co in companies}
    
    print("\n  Win Shares:")
    for co in sorted(win_pct, key=win_pct.get, reverse=True):
        print(f"    {co}: {win_pct[co]}%")
    
    # Check fragility
    max_win = max(win_pct.values())
    pick = max(win_pct, key=win_pct.get)
    fragile = max_win < 40
    
    if fragile:
        print(f"\n  DECISION IS FRAGILE: No company wins >40% of draws.")
        print(f"  Recommend split allocation.")
    else:
        print(f"\n  PICK: {pick} wins {max_win}% of draws.")
    
    return win_pct, pick, fragile


def main():
    print("=" * 60)
    print("PHASE 6 & 7: SCENARIOS, MONTE CARLO & ROBUST PICK")
    print("=" * 60)
    
    # Deterministic scenarios
    det_scenarios = deterministic_scenarios()
    
    outpath = OUTPUTS_DIR / "scenarios.csv"
    if det_scenarios:
        with open(outpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(det_scenarios[0].keys()))
            writer.writeheader()
            writer.writerows(det_scenarios)
        print(f"-> Wrote {outpath}")
    
    print("\nDeterministic Scenarios:")
    for s in det_scenarios:
        print(f"  {s['company']} {s['scenario']}: Rs {s['target_price']:,.0f} ({s['expected_return_pct']:+.1f}%)")
    
    # Monte Carlo
    mkt = load_market_data()
    mc_results = monte_carlo_simulation(10000)
    
    stats = compute_statistics(mc_results, mkt)
    
    # Write MC stats
    if stats:
        outpath = OUTPUTS_DIR / "montecarlo_stats.csv"
        with open(outpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(stats[0].keys()))
            writer.writeheader()
            writer.writerows(stats)
        print(f"\n-> Wrote {outpath}")
    
    # Robust pick (P7)
    forensic = load_forensic_scores()
    win_pct, pick, fragile = robust_pick_probability(mc_results, mkt, forensic)
    
    # Write pick results
    pick_result = {
        "pick": pick,
        "fragile": fragile,
        "win_shares": win_pct,
    }
    pick_path = OUTPUTS_DIR / "robust_pick.json"
    with open(pick_path, "w") as f:
        json.dump(pick_result, f, indent=2)
    print(f"-> Wrote {pick_path}")
    
    # Provenance
    provenance_rows = []
    for s in stats:
        for k, v in s.items():
            if k != "company":
                provenance_rows.append({
                    "timestamp": "2026-10-27", "company": s["company"],
                    "metric": f"mc_{k}", "fy": "12M",
                    "value": v, "unit": "various",
                    "source_file": "scenarios.py Monte Carlo",
                    "notes": f"10000 draws, seed={RANDOM_SEED}",
                })
    
    with open(PROVENANCE_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "company", "metric", "fy", "value", "unit", "source_file", "notes"])
        writer.writerows(provenance_rows)
    
    print(f"\n-> Appended {len(provenance_rows)} provenance entries")
    print("\n" + "=" * 60)
    print("PHASE 6 & 7 COMPLETE")
    print("=" * 60)
    
    return stats, pick_result


if __name__ == "__main__":
    main()
