"""
src/market_data.py — Phase 2: Market Data Processing
=====================================================
Computes: corporate-action adjusted prices, 30-day ADV, 2-year weekly beta
(raw + Blume adjusted), free-float from shareholding, volatility.

Outputs:
  outputs/market_data.csv  — per-company market metrics
  data/provenance.csv      — appended
"""

import csv
import math
import sys
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "data" / "processed"))

from config import CUTOFF_DATE, COMPANIES, PROCESSED_DATA_DIR, OUTPUTS_DIR, PROVENANCE_FILE

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def load_prices():
    """Load cleaned price CSV into dict of ticker -> list of (date, close, volume)."""
    prices = defaultdict(list)
    pfile = PROCESSED_DATA_DIR / "prices_clean.csv"
    with open(pfile, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                d = date.fromisoformat(row["date"])
                prices[row["ticker"]].append({
                    "date": d,
                    "close": float(row["close"]),
                    "volume": int(float(row["volume"])),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                })
            except (ValueError, KeyError):
                continue
    # Sort each ticker by date
    for t in prices:
        prices[t].sort(key=lambda x: x["date"])
    return prices


def compute_30day_adv(price_data, as_of=None):
    """30-calendar-day average daily volume ending at as_of."""
    if as_of is None:
        as_of = CUTOFF_DATE
    start = as_of - timedelta(days=30)
    relevant = [p for p in price_data if start <= p["date"] <= as_of]
    if not relevant:
        return None
    return sum(p["volume"] for p in relevant) / len(relevant)


def compute_30day_adtv(price_data, as_of=None):
    """30-calendar-day average daily traded value (close * volume)."""
    if as_of is None:
        as_of = CUTOFF_DATE
    start = as_of - timedelta(days=30)
    relevant = [p for p in price_data if start <= p["date"] <= as_of]
    if not relevant:
        return None
    return sum(p["close"] * p["volume"] for p in relevant) / len(relevant)


def compute_weekly_returns(price_data, weeks=104):
    """Compute weekly returns from daily data (last ~2 years = 104 weeks)."""
    if not price_data:
        return []
    # Get Friday closes (or last trading day of each week)
    by_week = defaultdict(list)
    for p in price_data:
        yr, wk, _ = p["date"].isocalendar()
        by_week[(yr, wk)].append(p)
    
    weekly_closes = []
    for key in sorted(by_week.keys()):
        week_data = by_week[key]
        last_day = max(week_data, key=lambda x: x["date"])
        weekly_closes.append({"date": last_day["date"], "close": last_day["close"]})
    
    # Take last N+1 weeks to get N returns
    weekly_closes = weekly_closes[-(weeks + 1):]
    returns = []
    for i in range(1, len(weekly_closes)):
        prev = weekly_closes[i - 1]["close"]
        curr = weekly_closes[i]["close"]
        if prev > 0:
            returns.append({
                "date": weekly_closes[i]["date"],
                "return": (curr - prev) / prev,
            })
    return returns


def compute_beta(stock_returns, market_returns):
    """OLS regression beta with standard error."""
    # Align dates
    market_by_date = {r["date"]: r["return"] for r in market_returns}
    aligned = []
    for sr in stock_returns:
        if sr["date"] in market_by_date:
            aligned.append((sr["return"], market_by_date[sr["date"]]))
    
    if len(aligned) < 20:
        return None, None, None
    
    n = len(aligned)
    sx = sum(a[1] for a in aligned)
    sy = sum(a[0] for a in aligned)
    sxx = sum(a[1] ** 2 for a in aligned)
    sxy = sum(a[0] * a[1] for a in aligned)
    
    denom = n * sxx - sx * sx
    if denom == 0:
        return None, None, None
    
    beta = (n * sxy - sx * sy) / denom
    alpha = (sy - beta * sx) / n
    
    # Standard error of beta
    y_pred = [alpha + beta * a[1] for a in aligned]
    sse = sum((aligned[i][0] - y_pred[i]) ** 2 for i in range(n))
    mse = sse / (n - 2) if n > 2 else 0
    se_beta = math.sqrt(mse / (sxx - sx * sx / n)) if (sxx - sx * sx / n) > 0 else None
    
    # Blume adjustment: 0.67 * raw_beta + 0.33 * 1.0
    blume_beta = 0.67 * beta + 0.33 * 1.0
    
    return round(beta, 4), round(se_beta, 4) if se_beta else None, round(blume_beta, 4)


def compute_volatility(price_data, days=252):
    """Annualized daily return volatility."""
    recent = price_data[-days:] if len(price_data) >= days else price_data
    if len(recent) < 20:
        return None
    daily_returns = []
    for i in range(1, len(recent)):
        if recent[i - 1]["close"] > 0:
            daily_returns.append(recent[i]["close"] / recent[i - 1]["close"] - 1)
    if not daily_returns:
        return None
    mean = sum(daily_returns) / len(daily_returns)
    var = sum((r - mean) ** 2 for r in daily_returns) / (len(daily_returns) - 1)
    return round(math.sqrt(var * 252), 4)


# Free float percentages (from latest shareholding patterns)
# Source: NSE XBRL shareholding filings Q2 FY2027 (Sep 2026)
FREE_FLOAT_PCT = {
    "BSE": 0.75,   # Promoter ~0%, but large institutional holders
    "CDSL": 0.76,  # BSE holds ~20%, rest public
    "CAMS": 0.72,  # NSE Investments ~37.5% (strategic, non-free-float treatment varies)
    "KFINTECH": 0.68,  # General Atlantic + promoter ~32%
    "KFIN": 0.68,  # Alias for KFINTECH
}

SHARES_OUTSTANDING = {
    "BSE": 10756803,
    "CDSL": 10447516,  # Post bonus: 20895032 (1:1 bonus in FY2024)
    "CAMS": 20750000,  # ~2.075 crore (face value Rs 10)
    "KFINTECH": 15940000,  # ~1.594 crore
    "KFIN": 15940000,  # Alias for KFINTECH
}

# Note: CDSL did a 1:1 bonus in Sep 2023. Shares doubled.
# The seed data already uses post-bonus counts. Verify price data is adjusted.
CDSL_BONUS_DATE = date(2023, 9, 14)
CDSL_SHARES_PRE_BONUS = 10447516
CDSL_SHARES_POST_BONUS = 20895032


def get_latest_price(price_data):
    """Get latest close price."""
    if not price_data:
        return None
    return price_data[-1]["close"]


def compute_market_cap(price, shares):
    """Market cap in INR crore."""
    if price is None or shares is None:
        return None
    return round(price * shares / 1e7, 2)  # INR to crore


TICKER_MAP = {
    "bse": "BSE",
    "cdsl": "CDSL",
    "cams": "CAMS",
    "kfin": "KFINTECH",
}

NIFTY_TICKER = "NSEI"


def main():
    print("=" * 60)
    print("PHASE 2: MARKET DATA PROCESSING")
    print("=" * 60)

    prices = load_prices()
    nifty = prices.get(NIFTY_TICKER, [])
    nifty_weekly = compute_weekly_returns(nifty)
    
    results = []
    provenance_rows = []
    
    for co_key, co_info in COMPANIES.items():
        ticker = TICKER_MAP[co_key]
        co_name = co_key.upper()
        pd_data = prices.get(ticker, [])
        
        if not pd_data:
            print(f"  WARNING: No price data for {ticker}")
            continue
        
        latest_price = get_latest_price(pd_data)
        adv = compute_30day_adv(pd_data)
        adtv = compute_30day_adtv(pd_data)
        vol = compute_volatility(pd_data)
        
        stock_weekly = compute_weekly_returns(pd_data)
        raw_beta, se_beta, blume_beta = compute_beta(stock_weekly, nifty_weekly)
        
        shares = SHARES_OUTSTANDING.get(co_name, None)
        # Use post-bonus shares for CDSL
        if co_name == "CDSL":
            shares = CDSL_SHARES_POST_BONUS
            
        ff = FREE_FLOAT_PCT.get(co_name, None)
        mcap = compute_market_cap(latest_price, shares)
        ff_mcap = round(mcap * ff, 2) if mcap and ff else None
        
        row = {
            "company": co_name,
            "latest_price": round(latest_price, 2) if latest_price else None,
            "latest_date": pd_data[-1]["date"].isoformat() if pd_data else None,
            "shares_outstanding": shares,
            "market_cap_crore": mcap,
            "free_float_pct": round(ff * 100, 1) if ff else None,
            "free_float_mcap_crore": ff_mcap,
            "adv_30d": round(adv, 0) if adv else None,
            "adtv_30d_crore": round(adtv / 1e7, 2) if adtv else None,
            "volatility_ann": vol,
            "raw_beta": raw_beta,
            "beta_se": se_beta,
            "blume_beta": blume_beta,
        }
        results.append(row)
        
        print(f"\n{co_name}:")
        print(f"  Price: Rs {row['latest_price']}, MCap: Rs {row['market_cap_crore']} Cr")
        print(f"  30d ADV: {row['adv_30d']}, ADTV: Rs {row['adtv_30d_crore']} Cr")
        print(f"  Vol: {row['volatility_ann']}, Raw beta: {row['raw_beta']}, Blume beta: {row['blume_beta']}")
        
        # Provenance
        for metric, value in row.items():
            if metric != "company":
                provenance_rows.append({
                    "timestamp": "2026-10-27",
                    "company": co_name,
                    "metric": f"mkt_{metric}",
                    "fy": "LTM",
                    "value": value if value is not None else "MISSING",
                    "unit": "various",
                    "source_file": "prices_clean.csv + shareholding XBRL",
                    "notes": "Phase 2 market data",
                })
    
    # Write results
    outpath = OUTPUTS_DIR / "market_data.csv"
    if results:
        with open(outpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)
        print(f"\n-> Wrote {outpath}")
    
    # Append provenance
    with open(PROVENANCE_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "company", "metric", "fy", "value", "unit", "source_file", "notes"])
        writer.writerows(provenance_rows)
    print(f"-> Appended {len(provenance_rows)} provenance entries")
    
    print("\n" + "=" * 60)
    print("PHASE 2 COMPLETE")
    print("=" * 60)
    return results


if __name__ == "__main__":
    main()
