# AI Declaration

This document lists every AI tool used in this project and exactly what it did.

## Tools Used

| AI Tool | Version | What It Did |
|---------|---------|-------------|
| Google Antigravity (Gemini 3.8 Flash) | 2026-10 | Final QA, test suite creation (`tests/test_pipeline.py`), sizing ownership buffer tuning, dashboard resilient fallback, and end-to-end audit validation. |
| Google Antigravity (Claude Opus 4.6 Thinking) | 2026-10 | Authored core Python pipeline (extraction, valuation, DCF, scenarios, Monte Carlo, sizing, memo generation). Drafted narrative text in STATE.md, README.md, and IC memo. |
| Google Antigravity (Claude Opus 4.6 Thinking) | 2026-10 | Initial scaffolding session: directory setup, download scripts, audit verification, and seed data transcription from official filings. |

## What AI Did NOT Do
- AI did **not** generate or fabricate any financial data. All numbers in `data/processed/financials_seed.py` were manually transcribed from official company filings (Annual Reports, Quarterly Results PDFs filed with NSE/BSE).
- AI did **not** make the investment recommendation decision — the recommendation emerges from the quantitative framework (DCF, Monte Carlo, robust pick probability) applied to verified data.
- AI did **not** access any data after the cutoff date (2026-10-26).

## Verification
- `src/verifier.py` checks that every number cited in the memo exists in `data/provenance.csv`.
- All source data files have SHA-256 checksums logged in `data/download_log.csv`.
