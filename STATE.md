# Project State & Execution Ledger

**Project**: Equity Research & Capital Allocation Recommendation (Rs 500 Crore Long-Only Mandate)  
**Universe**: BSE Ltd, CDSL, CAMS, KFin Technologies  
**Cutoff Date**: `2026-10-26` (Strictly Enforced)  
**Current Phase**: Phase 0 to Phase 13 Complete — All deliverables generated and verified  
**Last Updated**: 2026-10-27

---

## 1. Phase Progress Checklist

- [x] **P0 Audit and Setup**: Repo scaffolded, dependencies installed, files audited across directories, `COVERAGE_REPORT.md` generated with **READY** verdict.
- [x] **P1 Extraction and Validation**: 5 FY financials (P&L, Balance Sheet, Cash Flow) standalone + consolidated parsed into `data/processed/`, units normalisation, subtotal balance checks, industry time-series structuring, `data/provenance.csv` created.
- [x] **P2 Corporate Actions and Market Data**: Price adjustments, 30-day ADV, 2-year weekly beta (raw + Blume), free-float computation, ownership caps. Output in `outputs/market_data.csv`.
- [x] **P3 Driver Models (`src/drivers.py`)**: Operating leverage & derivatives sensitivity for BSE, account/transaction elasticity for CDSL, AUM yields & non-MF diversification for CAMS & KFin. Output in `outputs/driver_models.csv`.
- [x] **P4 Valuation**: 5-year integrated 3-statement forecast (`forecast.py`), FCFF DCF (`dcf_results.csv`), Multiples & peer benchmarking (`relative_valuation.csv`), live formula export to `outputs/valuation.xlsx`.
- [x] **P5 Forensics (`src/quality.py`)**: Beneish M-score, accruals ratio, CFO/EBITDA, related-party deep dive, regulatory reserve deductions. Output in `outputs/forensic_scores.csv`.
- [x] **P6 Scenarios, Shocks, Monte Carlo**: Discrete shock catalogue, 10,000 joint draws with explicit correlation matrix in `src/scenarios.py`. Output in `outputs/scenarios.csv`, `outputs/montecarlo_stats.csv`.
- [x] **P7 Robust Pick Probability**: Winner frequency across 10,000 draws, break-even flip sensitivities, fixed decision rules. Output in `outputs/robust_pick.json`.
- [x] **P8 Liquidity and Sizing (`src/sizing.py`)**: Rs 500 Cr allocation execution plan, ADV participation, impact cost, iterative ownership constraint solver (<=4.9%). Output in `outputs/sizing.csv`.
- [x] **P9 Tripwires (`src/tripwires.py`)**: 3 observable monthly exit triggers per company with current distance from cutoff. Output in `outputs/tripwires.csv`.
- [x] **P10 War Room & Verifier (`src/warroom.py`, `src/verifier.py`)**: Multi-agent adversarial debate (`warroom_debate.csv`) strictly verified against provenance ledger (`outputs/verification_report.csv`).
- [x] **P11 Memo (`src/memo.py`)**: 2-page institutional IC investment memo PDF with selectable text (`memo/ic_memo.pdf`).
- [x] **P12 Streamlit Dashboard (`app/dashboard.py`)**: Interactive dashboard with scenario sliders, valuation, forensics, sizing, and warroom tabs.
- [x] **P13 Final QA & Packaging**: Clean reproduction pipeline validated, test suite `tests/test_pipeline.py` created, `AI_DECLARATION.md` and `README.md` documented.

---

## 2. Key Decisions & Rationale

1. **Strict Cutoff Date Assertion**: `CUTOFF_DATE = 2026-10-26` is programmatically asserted in `src/config.py`. All price histories, filings, and announcements occurring after this date are rejected.
2. **Consolidated Financials as Valuation Base**: Consolidated financial statements represent the entire economic entity (e.g., BSE includes ICCL and India INX; CDSL includes CVL and CCRL; KFin includes international subsidiaries). Standalone statements are extracted and preserved for operational reconciliation.
3. **Restatement Protocol**: When prior-year figures are restated in subsequent annual reports, the latest restated figures are used and recorded in the extraction ledger.
4. **Primary vs Secondary Sources**: Company filings from NSE/BSE archives and regulatory bodies (SEBI, RBI, AMFI) serve as primary ground truth. Yahoo Finance is used strictly for market pricing cross-checks.

---

## 3. Red Team: 5 Weakest Assumptions per Company

### BSE Limited
1. **Derivatives Revenue Resilience Under F&O Curbs**: Assumes that options premium volume does not drop precipitously beyond 30% following SEBI's weekly expiry restrictions (limiting to Sensex only) and minimum contract size hikes to Rs 15–20 lakhs.
2. **Pricing Power on Transaction Fees**: Assumes BSE can sustain its transaction fee rate after shifting from slab-based fees to a uniform "True to Label" rate without losing market share back to NSE.
3. **Clearing Corporation (ICCL) Capital Strain**: Assumes regulatory core settlement guarantee fund (Core SGF) requirements do not require massive equity infusions that trap cash away from shareholder dividends.
4. **Operating Leverage Reversal**: Assumes technology, colocation, and clearing costs are flexible, whereas exchange fixed costs can cause dramatic operating margin contraction if turnover drops.
5. **Colocation & Market Data Monopolies**: Assumes market data and connectivity fees will continue double-digit growth even if high-frequency trading (HFT) and algorithmic participation decreases under intraday margin checks.

### CDSL (Central Depository Services Ltd)
1. **Terminal Demat Account Growth Rate**: Assumes retail investor onboarding continues at >2 million monthly accounts, ignoring potential saturation in India's addressable retail investing demographic.
2. **Pledge / Unpledge and Transaction Volume Elasticity**: Assumes transaction revenue will remain immune to reduced secondary market cash and derivatives trading frequency.
3. **True to Label / Depository Participant (DP) Fee Compression**: Assumes SEBI or competition from NSDL will not compress the Rs 4–5 per debit transaction charge levied on DPs.
4. **CVL KYC Revenue Cyclicality**: Assumes CDSL Ventures' KYC verification revenue is recurring, whereas it is heavily front-loaded and tied to new IPOs and mutual fund account creation booms.
5. **Cybersecurity / Systemic Outage Liability**: Depository infrastructure outages carry asymmetric regulatory penalties and reputational flight risks to NSDL.

### CAMS (Computer Age Management Services)
1. **AUM Yield Compression (bps)**: Assumes asset-weighted fee yield stays resilient around 3.5–4.0 bps despite rapid institutional AUM growth and SEBI's repeated regulatory scrutiny on Mutual Fund Total Expense Ratios (TER).
2. **Passive / ETF Disintermediation**: Assumes actively managed equity funds maintain dominant share; passive index funds and direct indexing offer drastically lower RTA basis-point yields.
3. **Client Concentration Risk**: Top 5 mutual fund clients account for ~65% of serviced AUM; loss of a single mega AMC (e.g. via acquisition or in-house shift) impairs revenue irreversibly.
4. **Account Aggregator & TSP Non-MF Scaling**: Assumes significant margin expansion from non-MF businesses (CAMSPay, Account Aggregator, Insurance Repository), which currently face stiff fintech competition.
5. **Operating Cost Inflation**: Assumes physical branch network servicing PAN-India tier-2/3 retail investors can be rationalized without losing statutory service quality mandates.

### KFin Technologies
1. **International Expansion Execution Risk**: Assumes high-margin SaaS/RTA expansion in Southeast Asia and GCC can offset domestic AMC concentration, despite longer enterprise sales cycles and foreign exchange volatility.
2. **Contract Renewal Churn**: Assumes key AMC client renewals occur at parity without fee cuts during competitive rebidding against CAMS.
3. **Issuer Solutions Cyclicality**: Corporate registry and IPO processing revenues are cyclical and highly vulnerable to equity market drawdowns and IPO market freezes.
4. **Acquisition Integration / Goodwill Amortization**: Aggressive acquisitions (e.g. Hexagram, WebFormix) create technological debt and potential balance sheet write-down risks if integration lags.
5. **Promoter Overhang / Private Equity Exits**: General Atlantic and historical promoter sell-downs historically triggered market price volatility and overhang.

---

## 4. Audit & Delivery Status
- **Audit Findings**: Successfully resolved massive 37.9× share count misstatement for BSE (was 10.75M, true 407.88M), reconciling market cap from ₹3,613 Cr to ₹137,008 Cr and P/E from 1.5× to 55.1×. Fixed severe geometric diffusion drift bug in Monte Carlo model that previously produced fictitious +82,166% return.
- **Frontend UI Transformation**: Transformed web application to Midnight Navy (`#0B1220`) & Emerald Green (`#10B981`) institutional design system. Added tabbed valuation views, interactive DCF scenario simulator, multi-agent adversarial war room debate filters, thesis drilldown modals, and responsive navigation across all viewports.
- **Winner Determination**: Quantitative framework unequivocally identifies **CAMS Limited** (96.4% Monte Carlo win share, 29.6× P/E, 100/100 forensic score, zero SEBI F&O regulatory overhang).
- **Deliverables**:
  - `final_deliverables/Zeckathon_Final_Research_Report.pdf` (14 sections, selectable text, fully compliant)
  - `final_deliverables/Zeckathon_Investment_Committee_Memo.pdf` (2 pages, executive IC memo)
  - `final_deliverables/Zeckathon_Model_Audit_Report.md` (root cause, mathematical formula diffs)
  - `README.md` & `AI_DECLARATION.md` updated
  - Interactive website (`app/index.html`, `app/style.css`, `app/script.js`) fully transformed and verified
- **Tests**: `tests/test_pipeline.py` passes 8/8 tests in 0.11s.
- **Git Branch**: `audit-and-repair`
- **Blockers**: None. Delivery complete and verified.

