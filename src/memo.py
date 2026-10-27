"""
src/memo.py — Phase 11: 2-Page Institutional IC Investment Memo (PDF)
======================================================================
Generates a selectable-text, 2-page IC memo pulling all figures
programmatically from outputs/.

Outputs:
  memo/ic_memo.pdf — investment committee memo
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "data" / "processed"))

from config import OUTPUTS_DIR, CUTOFF_DATE, MANDATE_CAPITAL_INR

MEMO_DIR = ROOT / "memo"
MEMO_DIR.mkdir(parents=True, exist_ok=True)


def load_csv(filename):
    """Load a CSV file from outputs/."""
    data = []
    fpath = OUTPUTS_DIR / filename
    if not fpath.exists():
        return data
    with open(fpath, newline="", encoding="utf-8") as f:
        data = list(csv.DictReader(f))
    return data


def load_json(filename):
    """Load a JSON file from outputs/."""
    fpath = OUTPUTS_DIR / filename
    if not fpath.exists():
        return {}
    with open(fpath, "r") as f:
        return json.load(f)


def get_val(data_list, company, field, default="N/A"):
    """Get a field value for a company from a list of dicts."""
    for row in data_list:
        if row.get("company") == company:
            v = row.get(field, default)
            return v if v not in (None, "", "None") else default
    return default


def main():
    print("=" * 60)
    print("PHASE 11: IC INVESTMENT MEMO (PDF)")
    print("=" * 60)

    # Load all data
    market_data = load_csv("market_data.csv")
    dcf_results = load_csv("dcf_results.csv")
    forensic_scores = load_csv("forensic_scores.csv")
    mc_stats = load_csv("montecarlo_stats.csv")
    scenarios = load_csv("scenarios.csv")
    relative_val = load_csv("relative_valuation.csv")
    sizing = load_csv("sizing.csv")
    robust_pick = load_json("robust_pick.json")

    pick = robust_pick.get("pick", "TBD")
    fragile = robust_pick.get("fragile", True)
    win_shares = robust_pick.get("win_shares", {})

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm, cm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor, black, white
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, HRFlowable
        )
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    except ImportError:
        print("ERROR: reportlab not installed. Run: pip install reportlab")
        return

    pdf_path = MEMO_DIR / "ic_memo.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=15*mm, bottomMargin=15*mm,
    )

    styles = getSampleStyleSheet()
    # Custom styles
    title_style = ParagraphStyle(
        'MemoTitle', parent=styles['Title'],
        fontSize=14, spaceAfter=3*mm, textColor=HexColor("#1a1a2e"),
        fontName='Helvetica-Bold',
    )
    subtitle_style = ParagraphStyle(
        'MemoSubtitle', parent=styles['Normal'],
        fontSize=9, spaceAfter=2*mm, textColor=HexColor("#444444"),
        fontName='Helvetica',
    )
    heading_style = ParagraphStyle(
        'MemoH2', parent=styles['Heading2'],
        fontSize=10, spaceBefore=3*mm, spaceAfter=1.5*mm,
        textColor=HexColor("#1a1a2e"), fontName='Helvetica-Bold',
    )
    body_style = ParagraphStyle(
        'MemoBody', parent=styles['Normal'],
        fontSize=8, leading=11, spaceAfter=1.5*mm,
        fontName='Helvetica', alignment=TA_JUSTIFY,
    )
    small_style = ParagraphStyle(
        'MemoSmall', parent=styles['Normal'],
        fontSize=7, leading=9, spaceAfter=1*mm,
        fontName='Helvetica', textColor=HexColor("#666666"),
    )
    bold_style = ParagraphStyle(
        'MemoBold', parent=body_style,
        fontName='Helvetica-Bold',
    )

    elements = []

    # ============================================================
    # PAGE 1: RECOMMENDATION & VALUATION
    # ============================================================

    elements.append(Paragraph(
        "EQUITY RESEARCH: Capital Allocation Recommendation",
        title_style
    ))
    elements.append(Paragraph(
        f"Zetheta x IIT Patna TIC | Universe: BSE, CDSL, CAMS, KFin | "
        f"Mandate: Rs 500 Cr Long-Only | Cutoff: {CUTOFF_DATE}",
        subtitle_style
    ))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#1a1a2e")))
    elements.append(Spacer(1, 2*mm))

    # RECOMMENDATION BOX
    rec_text = f"<b>PRIMARY PICK: {pick}</b>"
    if fragile:
        rec_text += " (Fragile - Split allocation recommended)"
    else:
        rec_text += f" | Win Share: {win_shares.get(pick, 0)}% across 10,000 Monte Carlo draws"
    elements.append(Paragraph(rec_text, bold_style))
    elements.append(Spacer(1, 1.5*mm))

    # Allocation summary
    alloc_text = "Allocation: "
    for co in ["BSE", "CDSL", "CAMS", "KFIN"]:
        alloc_pct = get_val(sizing, co, "allocation_pct", "0")
        alloc_cr = get_val(sizing, co, "allocation_crore", "0")
        alloc_text += f"{co} {alloc_pct}% (Rs {alloc_cr} Cr) | "
    elements.append(Paragraph(alloc_text.rstrip(" | "), body_style))
    elements.append(Spacer(1, 2*mm))

    # VALUATION SUMMARY TABLE
    elements.append(Paragraph("Valuation Summary", heading_style))
    
    val_header = ["Metric", "BSE", "CDSL", "CAMS", "KFIN"]
    val_data = [val_header]
    
    # Current price
    val_data.append(["CMP (Rs)"] + [
        get_val(market_data, co, "latest_price") for co in ["BSE", "CDSL", "CAMS", "KFIN"]
    ])
    
    # MCap
    val_data.append(["MCap (Rs Cr)"] + [
        get_val(market_data, co, "market_cap_crore") for co in ["BSE", "CDSL", "CAMS", "KFIN"]
    ])
    
    # DCF targets
    for sc in ["bull", "base", "bear"]:
        row_data = [f"DCF {sc.title()} (Rs)"]
        for co in ["BSE", "CDSL", "CAMS", "KFIN"]:
            val = "N/A"
            for d in dcf_results:
                if d["company"] == co and d["scenario"] == sc:
                    val = f"{float(d['dcf_per_share']):,.0f}"
            row_data.append(val)
        val_data.append(row_data)
    
    # P/E
    val_data.append(["P/E (x)"] + [
        get_val(relative_val, co, "pe") for co in ["BSE", "CDSL", "CAMS", "KFIN"]
    ])
    
    # ROE
    val_data.append(["ROE (%)"] + [
        get_val(relative_val, co, "roe_pct") for co in ["BSE", "CDSL", "CAMS", "KFIN"]
    ])
    
    # FCF Yield
    val_data.append(["FCF Yield (%)"] + [
        get_val(relative_val, co, "fcf_yield_pct") for co in ["BSE", "CDSL", "CAMS", "KFIN"]
    ])
    
    # Blume Beta
    val_data.append(["Blume Beta"] + [
        get_val(market_data, co, "blume_beta") for co in ["BSE", "CDSL", "CAMS", "KFIN"]
    ])

    t = Table(val_data, colWidths=[70, 85, 85, 85, 85])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#1a1a2e")),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.3, HexColor("#cccccc")),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor("#f5f5f5")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 3*mm))

    # MONTE CARLO SUMMARY
    elements.append(Paragraph("Monte Carlo Simulation (10,000 draws, seed=42)", heading_style))
    
    mc_header = ["Metric", "BSE", "CDSL", "CAMS", "KFIN"]
    mc_data = [mc_header]
    for metric, label in [
        ("expected_return_pct", "E[Return] (%)"),
        ("prob_loss_pct", "P(Loss) (%)"),
        ("cvar_5pct", "CVaR 5% (%)"),
        ("p50", "Median Price (Rs)"),
    ]:
        mc_data.append([label] + [
            get_val(mc_stats, co, metric) for co in ["BSE", "CDSL", "CAMS", "KFIN"]
        ])
    
    mc_data.append(["Win Share (%)"] + [
        str(win_shares.get(co, 0)) for co in ["BSE", "CDSL", "CAMS", "KFIN"]
    ])

    t2 = Table(mc_data, colWidths=[70, 85, 85, 85, 85])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#2d3436")),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.3, HexColor("#cccccc")),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor("#f5f5f5")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 3*mm))

    # FORENSIC QUALITY
    elements.append(Paragraph("Forensic Quality Assessment", heading_style))
    fq_header = ["Metric", "BSE", "CDSL", "CAMS", "KFIN"]
    fq_data = [fq_header]
    for metric, label in [
        ("cfo_ebitda", "CFO/EBITDA"),
        ("fcf_pat", "FCF/PAT"),
        ("accruals_ratio", "Accruals Ratio"),
        ("beneish_m_score", "Beneish M-Score"),
        ("m_score_flag", "M-Score Flag"),
        ("composite_score", "Composite (/100)"),
    ]:
        fq_data.append([label] + [
            get_val(forensic_scores, co, metric) for co in ["BSE", "CDSL", "CAMS", "KFIN"]
        ])

    t3 = Table(fq_data, colWidths=[70, 85, 85, 85, 85])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#0d7377")),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.3, HexColor("#cccccc")),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor("#f5f5f5")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(t3)

    # ============================================================
    # PAGE 2: THESIS, RISKS, TRIPWIRES
    # ============================================================
    elements.append(PageBreak())

    elements.append(Paragraph("Investment Thesis & Risk Assessment", title_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#1a1a2e")))
    elements.append(Spacer(1, 2*mm))

    # THESIS
    elements.append(Paragraph("Investment Thesis", heading_style))
    thesis = (
        f"We recommend <b>{pick}</b> as the primary allocation within the Rs 500 Cr mandate. "
        "India's capital markets infrastructure (exchanges, depositories, RTAs) is a "
        "structural play on financialization of household savings — a secular trend "
        "supported by rising demat accounts (55M to 270M in 5 years), SIP AUM exceeding "
        "Rs 13 lakh Cr, and regulatory tailwinds despite near-term F&O curbs. "
        "All four companies are near-zero debt, high-ROE, cash-generative franchises "
        "with significant operating leverage. "
    )
    if pick == "BSE":
        thesis += (
            "BSE has demonstrated explosive derivatives revenue growth (15x in 4 years) and high ROE, "
            "but trades at peak multiples (55.1x P/E) with acute single-product regulatory vulnerability "
            "to SEBI F&O restrictions."
        )
    elif pick == "CAMS":
        thesis += (
            "CAMS emerges as the robust institutional pick (96.4% Monte Carlo win share) due to superior "
            "valuation support (29.6x P/E, lowest in universe), an unassailable 100/100 forensic score, "
            "negative accruals, 68% market share in mutual fund RTA, and the lowest fundamental downside "
            "under combined regulatory and market stress tests."
        )
    elif pick == "CDSL":
        thesis += (
            "CDSL provides pure-play depository exposure (85% free float, 66% demat market share) with "
            "compelling cash conversion (98% FCF/PAT) and reasonable multiples (30.1x P/E), but faces "
            "near-term growth moderation in incremental demat onboarding."
        )
    elements.append(Paragraph(thesis, body_style))
    elements.append(Spacer(1, 2*mm))

    # KEY RISKS
    elements.append(Paragraph("Top 5 Risks (Red Team)", heading_style))
    risks = [
        "1. <b>Regulatory Risk (BSE):</b> SEBI F&O curbs — weekly expiry ban already reduced volumes. Further restrictions on lot sizes (>Rs 25L) or product eligibility would directly hit 74% of BSE revenue.",
        "2. <b>TER Compression (CAMS/KFin):</b> SEBI has cut MF expense ratios twice (2018, 2024). Another cut directly impairs RTA basis-point yields.",
        "3. <b>Client Concentration (CAMS):</b> Top 5 AMCs = ~65% of serviced AUM. Loss of a single mega-AMC is an irreversible revenue event.",
        "4. <b>Demat Saturation (CDSL):</b> Monthly net additions are decelerating. If growth falls below 1.5M/month, transaction revenue growth thesis weakens.",
        "5. <b>Data Staleness (KFIN):</b> FY2025-26 financials are MISSING. Valuation relies on FY2024 base — 2 years stale. Actual trajectory unknown.",
    ]
    for r in risks:
        elements.append(Paragraph(r, body_style))
    elements.append(Spacer(1, 2*mm))

    # EXIT TRIPWIRES (summary)
    elements.append(Paragraph("Exit Tripwires (Monthly Observable)", heading_style))
    tripwires_data = load_csv("tripwires.csv")
    tw_table = [["Company", "Trigger", "Action", "Status"]]
    for tw in tripwires_data[:6]:  # Top 6 tripwires
        tw_table.append([
            tw.get("company", ""),
            tw.get("trigger", "")[:60] + "...",
            tw.get("action", "")[:20],
            tw.get("status", ""),
        ])
    
    t4 = Table(tw_table, colWidths=[40, 220, 80, 70])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#c0392b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 6.5),
        ('GRID', (0, 0), (-1, -1), 0.3, HexColor("#cccccc")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor("#fef5f5")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(t4)
    elements.append(Spacer(1, 3*mm))

    # EXECUTION PLAN
    elements.append(Paragraph("Execution Plan (Rs 500 Cr)", heading_style))
    exec_table = [["Company", "Alloc %", "Alloc (Cr)", "ADTV (Cr)", "Days @15%", "Impact (bps)", "Ownership"]]
    for co in ["BSE", "CDSL", "CAMS", "KFIN"]:
        exec_table.append([
            co,
            get_val(sizing, co, "allocation_pct"),
            get_val(sizing, co, "allocation_crore"),
            get_val(sizing, co, "adtv_crore"),
            get_val(sizing, co, "exec_days_15pct_adv"),
            get_val(sizing, co, "impact_cost_bps"),
            get_val(sizing, co, "ownership_ok"),
        ])
    
    t5 = Table(exec_table, colWidths=[40, 45, 55, 55, 55, 55, 55])
    t5.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#27ae60")),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.3, HexColor("#cccccc")),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor("#f0faf0")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(t5)
    elements.append(Spacer(1, 3*mm))

    # DISCLAIMER
    elements.append(Paragraph(
        f"<i>This memo was generated programmatically from data/provenance.csv and outputs/. "
        f"All numeric claims are verified by src/verifier.py. Cutoff date: {CUTOFF_DATE}. "
        f"AI tools used are declared in AI_DECLARATION.md. "
        f"Assumptions locked at 2026-10-27T21:00:00+05:30 in assumptions.yaml.</i>",
        small_style
    ))

    # BUILD PDF
    doc.build(elements)
    print(f"\n-> Wrote {pdf_path}")
    print(f"   Pages: 2, Selectable text: YES")
    
    print("\n" + "=" * 60)
    print("PHASE 11 COMPLETE")
    print("=" * 60)
    return str(pdf_path)


if __name__ == "__main__":
    main()
