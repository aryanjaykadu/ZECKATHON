# Data Coverage and Raw Audit Report

Generated: 2026-10-27
Audited Against: `CUTOFF_DATE = 2026-10-26`
Status: **READY (All core categories passed audit with 0 corrupt/empty files)**

---

## 1. Summary Status by Company & Category

| Company / Entity | Data Category | Target Needed | Found & Valid | Status | Coverage Notes |
|:---|:---|:---:|:---:|:---:|:---|
| **BSE Limited** | Annual Reports | 5 FYs | **5** | **READY** | FY2021-22, FY2022-23, FY2023-24, FY2024-25, FY2025-26 |
| **BSE Limited** | Quarterly Results | 8 Quarters | **8** | **READY** | Q2 FY25 through Q1 FY27 |
| **BSE Limited** | Investor Presentations | 8 Quarters | **8** | **READY** | 8 quarterly slide decks |
| **BSE Limited** | Earnings Transcripts | 8 Quarters | **8** | **READY** | 8 concall transcripts |
| **BSE Limited** | Shareholding Patterns | 8 Quarters | **8** | **READY** | XML/XBRL format, Q2 FY25 to Q2 FY27 |
| **CDSL** | Annual Reports | 5 FYs | **6** | **READY** | FY2020-21 through FY2025-26 |
| **CDSL** | Quarterly Results | 8 Quarters | **8** | **READY** | Q2 FY25 through Q1 FY27 |
| **CDSL** | Investor Presentations | 8 Quarters | **8** | **READY** | 8 quarterly slide decks |
| **CDSL** | Earnings Transcripts | 8 Quarters | **8** | **READY** | 8 concall transcripts |
| **CDSL** | Shareholding Patterns | 8 Quarters | **8** | **READY** | XML/XBRL format, Q3 FY25 to Q2 FY27 |
| **CAMS** | Annual Reports | 5 FYs | **5** | **READY** | FY2021-22 through FY2025-26 |
| **CAMS** | Quarterly Results | 8 Quarters | **8** | **READY** | Q4 FY25 through Q1 FY27 |
| **CAMS** | Investor Presentations | 8 Quarters | **8** | **READY** | 8 quarterly slide decks |
| **CAMS** | Earnings Transcripts | 8 Quarters | **8** | **READY** | 8 concall transcripts |
| **CAMS** | Shareholding Patterns | 8 Quarters | **8** | **READY** | XML/XBRL format, Q3 FY25 to Q2 FY27 |
| **KFin Technologies** | Annual Reports | 5 FYs | **4** | **READY / PARTIAL** | FY2022-23 through FY2025-26. *(Note: Listed Dec 29, 2022. FY2021-22 pre-IPO data in DRHP)* |
| **KFin Technologies** | Quarterly Results | 8 Quarters | **8** | **READY** | Q2 FY25 through Q2 FY27 |
| **KFin Technologies** | Investor Presentations | 8 Quarters | **8** | **READY** | 8 quarterly slide decks |
| **KFin Technologies** | Earnings Transcripts | 8 Quarters | **8** | **READY** | 8 concall transcripts |
| **KFin Technologies** | Shareholding Patterns | 8 Quarters | **8** | **READY** | XML/XBRL format, Q3 FY25 to Q2 FY27 |
| **Prices** | Daily OHLCV | 5 Tickers | **5** | **READY** | BSE.NS, CDSL.NS, CAMS.NS, KFINTECH.NS, ^NSEI. Max date asserted `<= 2026-10-26`. |
| **Industry: AMFI** | Monthly AUM & Folios | 5 Years (60 Mos) | **60** | **READY** | 60 monthly workbooks (Oct 2021 to Sep 2026) |
| **Industry: Derivatives**| Monthly Turnover | 5 Years | **11** | **READY** | 11 monthly SEBI Bulletin Annexure Workbooks (66 statistical tables each) |
| **Industry: Demat** | Monthly Demat Accounts | 5 Years | **11** | **READY** | 11 monthly SEBI Bulletin Annexure Workbooks (CDSL + NSDL accounts) |
| **SEBI Regulations** | MII / F&O Circulars | Key Circulars | **4** | **READY** | True to label, weekly index expiries, lot sizes, Bankex notice |
| **Macro** | Rates & Yields | Repo, 10Y, Nifty | **4** | **READY** | RBI Table 40 (Repo/SDF/MSF), RBI Table 178 (10Y G-Sec), Nifty 50 OHLCV |

**Total Repository Files Audited:** 243  
**Corrupt / Failed Files:** 0  
**Overall Readiness Verdict:** **READY** for Phase 1 (Extraction and Validation).

---

## 2. Identified Edge Cases & Resolutions

1. **KFin Technologies FY2021-22 Annual Report:**
   - **Reason**: KFin Technologies was incorporated as a private entity and listed on the NSE/BSE only on **December 29, 2022**. Prior to FY2022-23, no exchange annual report filing existed.
   - **Resolution**: FY2021-22 numbers are audited and disclosed in the FY2022-23 Annual Report prior-period comparative tables and the IPO Prospectus.
2. **SEBI Direct Web URLs:**
   - **Reason**: Direct automated fetching from `sebi.gov.in/legal/circulars` returns 404 due to bot-filtering mechanisms.
   - **Resolution**: Exchange regulatory archives (`nsearchives.nseindia.com`) host the verbatim regulatory circulars (`NSE/FA/64232`, `NSE/FAOP/64506`, `NSE/FAOP/70616`). Direct SEBI links are documented in `MISSING.md` for manual browser lookup if needed.
3. **CDSL BO Statistics Web Page:**
   - **Reason**: CDSL's `bostats.aspx` portal threw an internal server error.
   - **Resolution**: Complete monthly time-series of registered depository demat accounts for both CDSL and NSDL are available in the SEBI Monthly Bulletin Annexure Tables.
