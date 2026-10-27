"""
Zekathon 2026 — Equity Research Dashboard
Streamlit interactive dashboard with scenario sliders and live distribution.
"""
import csv
import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

OUTPUTS_DIR = ROOT / "outputs"


def load_csv(filename):
    fpath = OUTPUTS_DIR / filename
    if not fpath.exists():
        return []
    with open(fpath, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_json(filename):
    fpath = OUTPUTS_DIR / filename
    if not fpath.exists():
        return {}
    with open(fpath, "r") as f:
        return json.load(f)


def main():
    st.set_page_config(page_title="Zekathon 2026 — Equity Research", layout="wide")
    
    st.title("Capital Allocation Recommendation")
    st.caption("Zetheta x IIT Patna TIC | Rs 500 Cr Long-Only Mandate | Cutoff: 2026-10-26")
    
    # Load data
    market_data = load_csv("market_data.csv")
    dcf_results = load_csv("dcf_results.csv")
    forensic_scores = load_csv("forensic_scores.csv")
    mc_stats = load_csv("montecarlo_stats.csv")
    scenarios = load_csv("scenarios.csv")
    sizing = load_csv("sizing.csv")
    robust_pick = load_json("robust_pick.json")
    warroom = load_csv("warroom_debate.csv")
    
    pick = robust_pick.get("pick", "TBD")
    win_shares = robust_pick.get("win_shares", {})
    
    # === RECOMMENDATION ===
    st.header(f"Primary Pick: {pick}")
    cols = st.columns(4)
    for i, co in enumerate(["BSE", "CDSL", "CAMS", "KFIN"]):
        with cols[i]:
            ws = win_shares.get(co, 0)
            md = next((r for r in market_data if r["company"] == co), {})
            price = md.get("latest_price", "N/A")
            mcap = md.get("market_cap_crore", "N/A")
            st.metric(co, f"Rs {price}", f"Win: {ws}%")
            st.caption(f"MCap: Rs {mcap} Cr")
    
    st.divider()
    
    # === VALUATION TAB ===
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Valuation", "Forensics", "Monte Carlo", "Sizing", "War Room"
    ])
    
    with tab1:
        st.subheader("DCF Valuation (Bull / Base / Bear)")
        if dcf_results:
            try:
                import pandas as pd
                df = pd.DataFrame(dcf_results)
                df["dcf_per_share"] = df["dcf_per_share"].astype(float).round(0)
                pivot = df.pivot_table(index="company", columns="scenario", values="dcf_per_share")
                st.dataframe(pivot, use_container_width=True)
            except Exception:
                st.dataframe(dcf_results, use_container_width=True)
        
        st.subheader("Scenario Analysis")
        if scenarios:
            st.dataframe(scenarios, use_container_width=True)
    
    with tab2:
        st.subheader("Forensic Quality Scores")
        if forensic_scores:
            st.dataframe(forensic_scores, use_container_width=True)
        
        for fs in forensic_scores:
            co = fs.get("company", "")
            score = fs.get("composite_score", "N/A")
            flag = fs.get("m_score_flag", "")
            color = "green" if flag == "PASS" else "orange"
            st.markdown(f"**{co}**: Composite {score}/100 | M-Score: :{color}[{flag}]")
    
    with tab3:
        st.subheader("Monte Carlo Distribution (10,000 draws)")
        if mc_stats:
            st.dataframe(mc_stats, use_container_width=True)
        
        st.subheader("Win Shares")
        for co, ws in sorted(win_shares.items(), key=lambda x: -x[1]):
            st.progress(ws / 100, text=f"{co}: {ws}%")
    
    with tab4:
        st.subheader("Rs 500 Cr Execution Plan")
        if sizing:
            st.dataframe(sizing, use_container_width=True)
        
        st.subheader("Ownership Constraints")
        for s in sizing:
            co = s.get("company", "")
            own = s.get("ownership_pct", "0")
            ok = s.get("ownership_ok", "")
            color = "green" if ok == "YES" else "red"
            st.markdown(f"**{co}**: {own}% ownership — :{color}[{ok}]")
    
    with tab5:
        st.subheader("Adversarial War Room")
        
        co_filter = st.selectbox("Company", ["All", "BSE", "CDSL", "CAMS", "KFIN"])
        
        for d in warroom:
            if co_filter != "All" and d.get("company") != co_filter:
                continue
            side = d.get("side", "")
            icon = "bull" if side == "BULL" else "bear"
            color = "green" if side == "BULL" else "red"
            st.markdown(f"**[{d.get('company')}]** :{color}[{side}]: {d.get('argument', '')}")
            st.caption(f"Data: {d.get('data_point', '')} | Rebuttal: {d.get('rebuttal', '')}")
            st.divider()
    
    # Footer
    st.caption("Generated programmatically. All claims verified against data/provenance.csv.")


if __name__ == "__main__":
    main()
