# Handoff & Transfer Prompt

If switching to another laptop or session, provide the prompt below to resume immediately with full context:

```markdown
# Zeckathon 2026 Equity Research — Resume & Final Polish Mission

## 1. Context & Architecture
We are completing the Zeckathon 2026 Equity Research Hackathon project (Zetheta x IIT Patna TIC).
- **Mandate**: Rs 500 Crore Long-Only across BSE Ltd, CDSL, CAMS, KFin Technologies
- **Strict Cutoff Rule**: `2026-10-26` (Programmatically enforced via `src/config.py:assert_before_cutoff`)
- **Key Decision**: Primary Pick is BSE (99.3% win share in 10,000-draw Monte Carlo). All positions respect strict <4.9% ownership and <10% free-float caps. Remaining 15.4% held as cash buffer.

## 2. Current Status
- All 14 analytical phases (P0 through P13) are complete:
  - Financial extraction, normalisation, and provenance tracking (`data/provenance.csv`)
  - Drivers, forecasts, DCF, Reverse DCF, scenarios, Monte Carlo (`outputs/`)
  - Forensics (Beneish M-Score, accruals, CFO/EBITDA)
  - Sizing & liquidity execution plan (`outputs/sizing.csv`)
  - Tripwires & adversarial war room (`outputs/tripwires.csv`, `outputs/warroom_debate.csv`)
  - Automated verifier (`src/verifier.py` -> `outputs/verification_report.csv`)
  - Institutional IC Investment Memo 2-page PDF (`memo/ic_memo.pdf`)
  - Interactive Streamlit Dashboard (`app/dashboard.py`)
  - Automated test suite (`tests/test_pipeline.py`)

## 3. Immediate Next Steps / Commands to Run
1. Verify the pipeline cleanly reproduces:
   ```powershell
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
   ```
2. Run the test suite:
   ```powershell
   .venv\Scripts\python.exe -m pytest tests/ -v
   ```
3. Test dashboard launch:
   ```powershell
   .venv\Scripts\python.exe -m streamlit run app/dashboard.py
   ```
4. Do final check of `AI_DECLARATION.md`, `README.md`, and `STATE.md`.
```
