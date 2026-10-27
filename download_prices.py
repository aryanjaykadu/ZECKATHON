"""Download daily OHLCV data via yfinance and log to download_log.csv."""
import yfinance as yf
import pandas as pd
import hashlib, csv, os
from datetime import datetime, date

CUTOFF = date(2026, 10, 26)
END_EXCLUSIVE = "2026-10-27"   # yfinance end is exclusive
START = "2016-10-27"           # ~10 years, covers 5-year need with margin

TICKERS = {
    "BSE.NS":      "BSE Ltd",
    "CDSL.NS":     "CDSL",
    "CAMS.NS":     "CAMS",
    "KFINTECH.NS": "KFin Technologies",
    "^NSEI":       "Nifty 50 Index",
}

OUT_DIR = os.path.join("data", "raw", "prices")
LOG_FILE = os.path.join("data", "download_log.csv")
TODAY = datetime.now().strftime("%Y-%m-%d")

os.makedirs(OUT_DIR, exist_ok=True)

for ticker, name in TICKERS.items():
    print(f"Downloading {ticker} ({name})...")
    df = yf.download(ticker, start=START, end=END_EXCLUSIVE, auto_adjust=True)
    if df.empty:
        print(f"  WARNING: No data for {ticker}")
        continue

    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Assert max date <= CUTOFF
    max_date = df.index.max().date()
    assert max_date <= CUTOFF, f"Max date {max_date} exceeds cutoff {CUTOFF}"
    print(f"  Date range: {df.index.min().date()} to {max_date}, rows={len(df)}")

    fname = f"{ticker.replace('^','').replace('.','_')}_daily_ohlcv.csv"
    fpath = os.path.join(OUT_DIR, fname)
    df.to_csv(fpath)

    sha = hashlib.sha256(open(fpath, "rb").read()).hexdigest()
    with open(LOG_FILE, "a", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            fname, name, "daily_ohlcv",
            f"yfinance:{ticker}", "Yahoo Finance (yfinance)",
            f"{df.index.min().date()} to {max_date}", TODAY, sha,
            f"Rows={len(df)}"
        ])
    print(f"  Saved: {fpath}")

print("\nPrice download complete.")
