// Zekathon 2026 — Capital Allocation & Equity Research Interactive Client
document.addEventListener('DOMContentLoaded', () => {
  // Mobile Navigation Toggle
  const mobileToggle = document.getElementById('mobileNavToggle');
  const navLinksContainer = document.getElementById('navLinks');

  if (mobileToggle && navLinksContainer) {
    mobileToggle.addEventListener('click', () => {
      navLinksContainer.classList.toggle('mobile-open');
      const isExpanded = navLinksContainer.classList.contains('mobile-open');
      mobileToggle.setAttribute('aria-expanded', isExpanded);
    });

    // Close mobile nav when clicking any link
    document.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        navLinksContainer.classList.remove('mobile-open');
        mobileToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Active Navigation Spy on Scroll
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');

  const onScroll = () => {
    const scrollPos = window.scrollY + 120;
    sections.forEach(section => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      const id = section.getAttribute('id');
      if (scrollPos >= top && scrollPos < top + height) {
        navLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('active');
          }
        });
      }
    });
  };
  window.addEventListener('scroll', onScroll, { passive: true });

  // Tab System for Valuation Views
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      tabButtons.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const activePane = document.getElementById(targetTab);
      if (activePane) {
        activePane.classList.add('active');
      }
    });
  });

  // Adversarial War Room Filtering
  const warroomFilterBtns = document.querySelectorAll('.warroom-filter-btn');
  const warroomCards = document.querySelectorAll('.warroom-card');

  warroomFilterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      warroomFilterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.getAttribute('data-filter');
      warroomCards.forEach(card => {
        if (filter === 'all' || card.getAttribute('data-company') === filter) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  // Interactive DCF Sensitivity Simulator Form
  const calcSelect = document.getElementById('calcCompany');
  const calcGrowth = document.getElementById('calcGrowth');
  const calcWacc = document.getElementById('calcWacc');
  const calcOutput = document.getElementById('calcOutputTarget');
  const calcDiff = document.getElementById('calcDiffPercent');

  const baseValues = {
    CAMS: { price: 661.5, baseDcf: 278.8, wacc: 14.75, g: 5.0 },
    CDSL: { price: 1196.0, baseDcf: 447.2, wacc: 16.34, g: 5.0 },
    BSE: { price: 3359.0, baseDcf: 596.2, wacc: 14.76, g: 5.0 },
    KFIN: { price: 829.0, baseDcf: 206.3, wacc: 14.83, g: 5.0 }
  };

  function updateSimulator() {
    if (!calcSelect || !calcGrowth || !calcWacc || !calcOutput || !calcDiff) return;

    const co = calcSelect.value;
    const base = baseValues[co] || baseValues.CAMS;
    const gVal = parseFloat(calcGrowth.value) || 5.0;
    const waccVal = parseFloat(calcWacc.value) || 14.75;

    // First-order Taylor approximation for terminal value sensitivity
    // Value is inversely proportional to (WACC - g)
    const baseDenom = (base.wacc / 100) - (base.g / 100);
    const newDenom = Math.max(0.02, (waccVal / 100) - (gVal / 100));
    const factor = (baseDenom / newDenom);
    
    // Terminal value is ~65% of EV, PV of FCFFs is ~35% (discounted at new WACC)
    const adjustedDcf = base.baseDcf * (0.35 * (base.wacc / waccVal) + 0.65 * factor);
    const formattedDcf = adjustedDcf.toFixed(1);
    const diffPct = (((adjustedDcf - base.price) / base.price) * 100).toFixed(1);

    calcOutput.textContent = `₹${formattedDcf}`;
    calcDiff.textContent = `${diffPct > 0 ? '+' : ''}${diffPct}% vs Market (₹${base.price})`;
    calcDiff.className = `modal-mono font-mono ${diffPct >= 0 ? 'text-positive' : 'text-negative'}`;
  }

  if (calcSelect && calcGrowth && calcWacc) {
    calcSelect.addEventListener('change', () => {
      const co = calcSelect.value;
      const base = baseValues[co];
      if (base) {
        calcGrowth.value = base.g;
        calcWacc.value = base.wacc;
        updateSimulator();
      }
    });
    calcGrowth.addEventListener('input', updateSimulator);
    calcWacc.addEventListener('input', updateSimulator);
  }

  // Drilldown Modal Dialog Logic
  const modalBackdrop = document.getElementById('detailModal');
  const modalTitle = document.getElementById('modalTitle');
  const modalContent = document.getElementById('modalContent');
  const modalClose = document.getElementById('modalClose');

  const companyDetails = {
    CAMS: {
      title: "CAMS Limited — Investment Thesis & Proof Points",
      body: `
        <div class="modal-detail-section">
          <h4 style="color: var(--accent-emerald); margin-bottom: 8px;">Consensus Divergence & Moat</h4>
          <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
            CAMS commands a 68% AUM market share across Indian Mutual Funds with ~100% renewal rate and zero client defection in 15+ years. 
            At 29.6x trailing P/E and a 3.07% FCF yield, it requires only 34.9% 5Y FCFF CAGR to justify current price—the lowest hurdle in the coverage universe.
          </p>
        </div>
        <div class="modal-detail-section" style="margin-top: 16px;">
          <h4 style="color: var(--text-main); margin-bottom: 8px;">Audit & Governance Assurance</h4>
          <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
            Audited by S.R. Batliboi (EY). Beneish M-Score of -1.92 completely passes financial manipulation screens. Zero leverage and FCF/PAT conversion exceeding 91%.
          </p>
        </div>
      `
    },
    CDSL: {
      title: "CDSL — Central Depository Services",
      body: `
        <div class="modal-detail-section">
          <h4 style="color: var(--accent-emerald); margin-bottom: 8px;">Beneficiary of Demat Account Penetration</h4>
          <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
            CDSL holds 66% market share in demat accounts. Annual issuer fees generate recurring non-market revenues, while capex intensity remains minimal at 2.5%.
          </p>
        </div>
        <div class="modal-detail-section" style="margin-top: 16px;">
          <h4 style="color: var(--text-main); margin-bottom: 8px;">Key Monitorables</h4>
          <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
            Transaction fees remain cyclical with market turnover. M-Score is -1.77 (Investigate flag due to DSRI asset-growth surge), but audit is clean by Walker Chandiok.
          </p>
        </div>
      `
    },
    BSE: {
      title: "BSE Limited — Platform Moat vs Regulatory Risk",
      body: `
        <div class="modal-detail-section">
          <h4 style="color: var(--warning); margin-bottom: 8px;">Derivatives Hyper-Growth & Exposure</h4>
          <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
            Derivatives revenue has grown 15x over 4 years to 73.8% of total revenue. Trailing P/E of 55.1x requires an 81.1% reverse-DCF implied CAGR to justify price.
          </p>
        </div>
        <div class="modal-detail-section" style="margin-top: 16px;">
          <h4 style="color: var(--text-main); margin-bottom: 8px;">Governance & Sizing Justification</h4>
          <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
            Deloitte audited. Capped at ₹66.5 Cr (13.3%) allocation with clear exit tripwires (TW1-TW3) safeguarding capital against severe SEBI volume curbs.
          </p>
        </div>
      `
    },
    KFIN: {
      title: "KFin Technologies — SaaS Platform & Global RTA",
      body: `
        <div class="modal-detail-section">
          <h4 style="color: var(--accent-emerald); margin-bottom: 8px;">International Diversification</h4>
          <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
            Commands 32% domestic MF AUM plus major market shares in issuer solutions, pension, and international Southeast Asian RTA services.
          </p>
        </div>
        <div class="modal-detail-section" style="margin-top: 16px;">
          <h4 style="color: var(--text-main); margin-bottom: 8px;">Forensic Highlights</h4>
          <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
            Composite score 100/100, Beneish M-Score of -2.02 (PASS), CFO/EBITDA 85.7%, FCF/PAT 113.6%. Audited by MSKA (BDO).
          </p>
        </div>
      `
    }
  };

  document.querySelectorAll('.open-drilldown-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const co = btn.getAttribute('data-company');
      const details = companyDetails[co];
      if (details && modalBackdrop && modalTitle && modalContent) {
        modalTitle.textContent = details.title;
        modalContent.innerHTML = details.body;
        modalBackdrop.classList.add('open');
        modalBackdrop.setAttribute('aria-hidden', 'false');
      }
    });
  });

  if (modalClose && modalBackdrop) {
    modalClose.addEventListener('click', () => {
      modalBackdrop.classList.remove('open');
      modalBackdrop.setAttribute('aria-hidden', 'true');
    });

    modalBackdrop.addEventListener('click', (e) => {
      if (e.target === modalBackdrop) {
        modalBackdrop.classList.remove('open');
        modalBackdrop.setAttribute('aria-hidden', 'true');
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modalBackdrop.classList.contains('open')) {
        modalBackdrop.classList.remove('open');
        modalBackdrop.setAttribute('aria-hidden', 'true');
      }
    });
  }
});
