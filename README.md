# Zekathon 2026 — Capital Allocation & Equity Research

**Zetheta × IIT Patna TIC — Hackathon Submission**  
**Problem Statement 1:** Equity Research & Financial Consulting  
**Universe Covered:** BSE Limited, CDSL, CAMS, KFin Technologies  
**Mandate:** ₹500 Crore Long-Only Portfolio (12-Month Horizon)  
**Strict Cutoff Date:** `2026-10-26`  
**Primary Recommendation:** **CAMS Limited (CAMS.NS)** — 96.4% Monte Carlo Win Share  

---

## 1. Quick Start & Complete Reproduction

This repository is built for **100% deterministic reproducibility** from a clean clone. Dependencies are pinned and all random seeds are fixed (`RANDOM_SEED = 42`).

### Prerequisites
- Python 3.10+ (Windows / Linux / macOS)
- Standard tools (`git`, `make` or PowerShell)

### Installation & Execution
```powershell
# 1. Create and activate virtual environment
py -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Execute the full quantitative pipeline (P1 to P11)
python src/extract.py
python src/market_data.py
python src/drivers.py
python src/forecast.py
python src/quality.py
python src/scenarios.py
python src/sizing.py
python src/tripwires.py
python src/warroom.py
python src/verifier.py
python src/memo.py
python src/generate_full_report.py

# 4. Run automated test suite
pytest tests/ -v
```
*Alternatively, run `make run` followed by `make test`.*

---

## 2. Interactive Interfaces & Web Delivery

### Option A: Institution-Grade Liquid Glass Web Showcase (Recommended)
The submission includes a responsive web interface featuring glassmorphic design, dynamic 3D card tilt, interactive metric tracking, and direct PDF downloads:
```powershell
# Serve static web app locally
python -m http.server 8000 --directory app
```
Navigate to `http://localhost:8000` in any web browser.

### Option B: Streamlit Quantitative Dashboard
```powershell
streamlit run app/dashboard.py
```
Navigate to `http://localhost:8501`.

---

## 3. Official Deliverables Directory (`final_deliverables/`)

All primary competition submission deliverables reside in `final_deliverables/`:

1. **`Zeckathon_Final_Research_Report.pdf`**  
   - Comprehensive, 14-section institutional equity research report.  
   - Includes industry structure, competitive advantage, audited valuation multiples, 5-year integrated financial model for CAMS, DCF bridges, scenario analysis (-30% derivatives, -20% equity drawdown), 10,000-draw Monte Carlo distribution, forensic accounting ledgers, and observable monthly exit tripwires.  
   - Vector selectable text, dynamic page numbering, <20 MB (31.1 KB).

2. **`Zeckathon_Investment_Committee_Memo.pdf`**  
   - Concise 2-page executive investment committee memo.  
   - Features complete, un-truncated allocation, valuation, Monte Carlo, and tripwire summary tables pulling figures programmatically from `outputs/`.

3. **`Zeckathon_Model_Audit_Report.md`**  
   - Forensic technical audit report documenting the root cause of the previous numerical anomalies (BSE 37.9× share count understatement, exponential drift explosion in Monte Carlo, and ₹423 Cr under-allocation), exact code changes, and validation tests.

4. **`README.md`**  
   - Complete project overview, architecture, reproduction instructions, data provenance, and test commands.

5. **`AI_DECLARATION.md`**  
   - Transparent disclosure of AI assistance in accordance with hackathon rules.

---

## 4. Key Financial Audit Findings & Recommendation Summary

### Root Cause of Previous Anomalies
1. **Share Count Understatement:** BSE shares were hardcoded as 10.75M instead of the audited **407.88M shares** (Q2 FY2027 XBRL filing), artificially suppressing BSE market cap to ₹3,613 Cr (actual: **₹1,37,008 Cr**), distorting trailing P/E to 1.5× (actual: **55.1×**), and inflating DCF per share to ₹22,606 (actual: **₹596.2**).
2. **Diffusion Drift Explosion:** A linear percentage return was erroneously passed directly as an exponent in geometric Brownian motion diffusion, scaling median simulated prices to ₹10,54,076 (+82,166.9%). Fixing this to log-diffusion $\ln(\text{target}/\text{price})$ normalized simulations to economically defensible distributions.
3. **Allocation Deficit:** Replaced fragmented constraints with an iterative linear solver reconciling **exactly to ₹500.00 Crore (100.0%)**.

### The Investment Recommendation
- **Primary Pick:** **CAMS Limited** (60.0% Allocation / ₹300.00 Cr / 96.4% Monte Carlo Win Share).
- **Rationale:** 
  - **Valuation Margin of Safety:** Lowest P/E in coverage at **29.6×** (vs. BSE 55.1×, KFin 65.1×).
  - **Forensic Accounting Excellence:** Perfect **100/100 composite score**, negative accruals (-0.0125), CFO/EBITDA of 71.6%, clean audit by S.R. Batliboi (EY).
  - **Regulatory Resilience:** Operates a 68% mutual fund RTA duopoly with zero direct exposure to SEBI's F&O trading curbs or exchange flat-fee margin compression.
  - **Lowest Growth Hurdle:** Requires 34.9% p.a. 5-year FCFF growth to justify current market price (vs. BSE requiring 81.1% p.a.).

---

## 5. Automated Testing & Verification

The repository includes a comprehensive automated test suite verifying data provenance, cutoff date integrity, valuation formulas, and artifact integrity:

```powershell
pytest tests/ -v
```

### Verified Test Cases:
- `test_cutoff_date`: Enforces that zero data after `2026-10-26` is processed.
- `test_provenance_integrity`: Verifies evidence ledger has >750 verified entries.
- `test_outputs_exist`: Confirms all 14 required pipeline files are generated.
- `test_memo_exists`: Verifies the 2-page IC memo exists and has content.
- `test_sizing_constraints`: Reconciles ₹500 Cr deployment, verifying <4.9% ownership and <10% free-float compliance.
- `test_valuation_reconciliation`: Confirms market caps equal $P \times S / 10^7$ and P/E equals $P / \text{EPS}$ within 0.1 tolerance.
- `test_dcf_and_simulation_sanity`: Asserts all simulation outputs are finite, positive, and non-explosive.
- `test_final_deliverables_exist`: Confirms full research report and memo PDFs are compiled in `final_deliverables/`.

---

## 6. Pipeline Architecture

| Phase | Module | Functionality | Primary Output |
| :--- | :--- | :--- | :--- |
| **P1** | `src/extract.py` | Audited financial statements extraction | `data/provenance.csv` |
| **P2** | `src/market_data.py` | Prices, ADTV, volatilities, betas, and market caps | `outputs/market_data.csv` |
| **P3** | `src/drivers.py` | Segmental revenue drivers (turnover, demat, AAUM) | `outputs/driver_models.csv` |
| **P4** | `src/forecast.py` | 5-year integrated forecasts, DCF bridges, reverse DCF | `outputs/dcf_results.csv`, `relative_valuation.csv` |
| **P5** | `src/quality.py` | Forensic due diligence, Beneish M-Scores, accruals | `outputs/forensic_scores.csv` |
| **P6-P7** | `src/scenarios.py` | Stress tests, 10,000-draw Monte Carlo, robust pick ranking | `outputs/scenarios.csv`, `montecarlo_stats.csv` |
| **P8** | `src/sizing.py` | ₹500 Cr allocation solver, ADV participation, impact cost | `outputs/sizing.csv` |
| **P9** | `src/tripwires.py` | 3 observable monthly exit triggers per franchise | `outputs/tripwires.csv` |
| **P10** | `src/warroom.py` | Adversarial Red-Team bull/bear debate ledger | `outputs/warroom_debate.csv` |
| **P10a** | `src/verifier.py` | Claims verification against provenance ledger | `outputs/verification_report.csv` |
| **P11** | `src/memo.py` | Institutional 2-page IC Investment Memo compiler | `final_deliverables/Zeckathon_Investment_Committee_Memo.pdf` |
| **P11a**| `src/generate_full_report.py` | 14-section comprehensive research report compiler | `final_deliverables/Zeckathon_Final_Research_Report.pdf` |

---

## 7. Data Provenance & Known Limitations

1. **Cutoff Compliance:** All data is strictly anchored on or before `2026-10-26`.
2. **Primary Sources:** Audited company filings (BSE/NSE), SEBI bulletins, AMFI monthly disclosures, RBI Table 178.
3. **Known Limitation — KFin Reporting:** Audited Annual Reports for KFin Technologies are available up to FY2024; FY2025–26 detailed balance sheets were missing in public repositories. Valuations rely on FY2024 baseline projected forward under explicit growth assumptions.
4. **NSE Non-Listing:** While NSE commands ~90% of equity derivatives volume, it remains unlisted and is therefore excluded from direct capital deployment.
