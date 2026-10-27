# Zekathon 2026 — Equity Research & Capital Allocation

**Zetheta × IIT Patna TIC**  
**Universe**: BSE Ltd, CDSL, CAMS, KFin Technologies  
**Mandate**: Rs 500 Crore Long-Only  
**Cutoff Date**: 2026-10-26  

---

## Quick Start

```powershell
# Setup (once)
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt

# Run full pipeline (reproduces all outputs)
.venv\Scripts\python.exe src/extract.py
.venv\Scripts\python.exe src/market_data.py
.venv\Scripts\python.exe src/drivers.py
.venv\Scripts\python.exe src/forecast.py
.venv\Scripts\python.exe src/quality.py
.venv\Scripts\python.exe src/scenarios.py
.venv\Scripts\python.exe src/sizing.py
.venv\Scripts\python.exe src/tripwires.py
.venv\Scripts\python.exe src/warroom.py
.venv\Scripts\python.exe src/verifier.py
.venv\Scripts\python.exe src/memo.py

# Dashboard
.venv\Scripts\python.exe -m streamlit run app/dashboard.py
```

Or use `make run` from a clean clone.

---

## Pipeline Architecture

| Phase | Module | Output |
|-------|--------|--------|
| P1 | `src/extract.py` | `data/processed/financials_*.csv`, `data/provenance.csv` |
| P2 | `src/market_data.py` | `outputs/market_data.csv` |
| P3 | `src/drivers.py` | `outputs/driver_models.csv` |
| P4 | `src/forecast.py` | `outputs/forecasts.csv`, `dcf_results.csv`, `relative_valuation.csv`, `valuation.xlsx` |
| P5 | `src/quality.py` | `outputs/forensic_scores.csv` |
| P6-7 | `src/scenarios.py` | `outputs/scenarios.csv`, `montecarlo_stats.csv`, `robust_pick.json` |
| P8 | `src/sizing.py` | `outputs/sizing.csv` |
| P9 | `src/tripwires.py` | `outputs/tripwires.csv` |
| P10 | `src/warroom.py`, `src/verifier.py` | `outputs/warroom_debate.csv`, `verification_report.csv` |
| P11 | `src/memo.py` | `memo/ic_memo.pdf` |
| P12 | `app/dashboard.py` | Streamlit interactive dashboard |

---

## Key Design Decisions

1. **Cutoff Date Enforcement**: `CUTOFF_DATE = 2026-10-26` is programmatically asserted in `src/config.py`. All data after this date is rejected.
2. **Consolidated Financials**: Used as valuation base. Standalone preserved for reconciliation.
3. **Provenance Ledger**: Every number flows into `data/provenance.csv`. The verifier (`src/verifier.py`) checks all output claims against this ledger.
4. **Assumptions Locked**: All model parameters in `assumptions.yaml` timestamped before results were computed.
5. **Fixed Seed**: `RANDOM_SEED = 42` for reproducible Monte Carlo.
6. **Ownership Constraints**: Allocation capped at 4.9% ownership and 10% free-float per position.

---

## Data Sources

- **Primary**: Company filings from NSE/BSE archives, SEBI, RBI, AMFI
- **Pricing**: Yahoo Finance (OHLCV), cross-checked against exchange data
- **Seed Data**: Manually transcribed from audited Annual Reports and Quarterly Results

See `SOURCES.md` and `data/download_log.csv` for full provenance.

---

## AI Declaration

See `AI_DECLARATION.md`. AI tools authored all Python code and drafted narrative text. All financial data was manually transcribed from official filings. Investment recommendation emerges from the quantitative framework.

---

## Repository Structure

```
zekathon/
├── AGENTS.md              # Agent behavioral rules
├── AI_DECLARATION.md      # AI tool usage disclosure
├── assumptions.yaml       # Locked model assumptions
├── Makefile               # Build system
├── requirements.txt       # Python dependencies
├── src/                   # Source modules (P1-P11)
├── data/
│   ├── raw/               # Downloaded source files
│   ├── processed/         # Extracted financials, prices
│   └── provenance.csv     # Evidence ledger
├── outputs/               # All computed outputs (CSV, XLSX, JSON)
├── memo/                  # IC investment memo PDF
├── app/                   # Streamlit dashboard
└── tests/                 # Test suite
```
