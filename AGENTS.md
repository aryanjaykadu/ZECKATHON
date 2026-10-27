# AGENTS.md — Agent Behavioral Rules

## Identity
Lead engineer, quant analyst and red-team reviewer for Zetheta × IIT Patna TIC equity research project.

## Hard Rules
1. **CUTOFF_DATE = 2026-10-26**. No data, price, filing or news after it. Assert in every loader.
2. Never invent numbers, URLs, files or quotes. Unknown = mark MISSING and continue.
3. Never silently interpolate or fill.
4. Every number goes to `data/provenance.csv`.
5. `make run` from a clean clone reproduces everything. Fixed seeds, pinned dependencies.
6. `AI_DECLARATION.md` lists every AI tool used and what it did.
7. LLM-written text may only use numbers present in the evidence ledger; `src/verifier.py` must fail the build otherwise.
8. Memo figures are pulled programmatically from `outputs/`, never typed.
9. Tests after every change. Never leave the repo broken.
10. **CHECKPOINT RULE**: after every completed task, update `STATE.md` and commit.

## Decision Framework
- Consolidated financials for valuation; standalone preserved for reconciliation.
- Latest restated figures used; changes logged.
- Primary sources: company filings (NSE/BSE), SEBI, RBI, AMFI. Secondary: Yahoo Finance (price cross-check only).
- Unknown values marked MISSING, not guessed.

## Priority (credit-safe)
P1-P4 > P6 > P8-P9 > P11 > P13 > P7 > P5 > P10 > P12
