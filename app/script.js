// Zekathon 2026 — Capital Allocation & Institutional Equity Research Client
document.addEventListener('DOMContentLoaded', () => {
  // -------------------------------------------------------------
  // 1. Cursor-following Ambient Light & Card Lighting
  // -------------------------------------------------------------
  const isTouchDevice = () => window.matchMedia('(pointer: coarse)').matches;
  const prefersReducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!isTouchDevice() && !prefersReducedMotion()) {
    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight * 0.3;
    let currentX = mouseX;
    let currentY = mouseY;
    let isTracking = true;

    // Track mouse position globally
    window.addEventListener('pointermove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    }, { passive: true });

    // Handle cursor leaving/entering window
    document.addEventListener('mouseleave', () => {
      isTracking = false;
      const spotlight = document.querySelector('.cursor-ambient-spotlight');
      if (spotlight) spotlight.style.opacity = '0';
    });

    document.addEventListener('mouseenter', () => {
      isTracking = true;
      const spotlight = document.querySelector('.cursor-ambient-spotlight');
      if (spotlight) spotlight.style.opacity = '1';
    });

    // Smooth cursor lighting animation loop with requestAnimationFrame
    const updateCursorLighting = () => {
      if (isTracking && !document.hidden) {
        currentX += (mouseX - currentX) * 0.15;
        currentY += (mouseY - currentY) * 0.15;
        document.documentElement.style.setProperty('--mouse-x', `${currentX.toFixed(1)}px`);
        document.documentElement.style.setProperty('--mouse-y', `${currentY.toFixed(1)}px`);
      }
      requestAnimationFrame(updateCursorLighting);
    };
    requestAnimationFrame(updateCursorLighting);

    // Interactive card lighting relative to pointer coordinates
    const interactivePanels = document.querySelectorAll('.interactive-panel, .company-card, .forensic-card, .hero-conviction-card');
    interactivePanels.forEach(panel => {
      panel.addEventListener('pointermove', (e) => {
        const rect = panel.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        panel.style.setProperty('--card-x', `${x}px`);
        panel.style.setProperty('--card-y', `${y}px`);
      }, { passive: true });
    });
  }

  // -------------------------------------------------------------
  // 2. Mobile Navigation Toggle & Accessibility
  // -------------------------------------------------------------
  const mobileToggle = document.getElementById('mobileNavToggle');
  const navLinksContainer = document.getElementById('navLinks');

  if (mobileToggle && navLinksContainer) {
    mobileToggle.addEventListener('click', () => {
      const isCurrentlyOpen = navLinksContainer.classList.contains('mobile-open');
      navLinksContainer.classList.toggle('mobile-open');
      const isExpanded = !isCurrentlyOpen;
      mobileToggle.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
      mobileToggle.innerHTML = isExpanded ? '✕ Close' : '☰ Menu';
    });

    // Close mobile nav when clicking any link
    document.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        navLinksContainer.classList.remove('mobile-open');
        mobileToggle.setAttribute('aria-expanded', 'false');
        mobileToggle.innerHTML = '☰ Menu';
      });
    });
  }

  // -------------------------------------------------------------
  // 3. Active Navigation Spy on Scroll
  // -------------------------------------------------------------
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');

  const onScroll = () => {
    const scrollPos = window.scrollY + 140;
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

  // -------------------------------------------------------------
  // 4. Tab System for Valuation Views
  // -------------------------------------------------------------
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      tabButtons.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      const activePane = document.getElementById(targetTab);
      if (activePane) {
        activePane.classList.add('active');
      }
    });
  });

  // -------------------------------------------------------------
  // 5. Adversarial War Room Filtering
  // -------------------------------------------------------------
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

  // -------------------------------------------------------------
  // 6. Interactive DCF Sensitivity Simulator Form
  // -------------------------------------------------------------
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
    calcDiff.textContent = `${diffPct > 0 ? '+' : ''}${diffPct}% vs Market (₹${base.price.toLocaleString('en-IN')})`;
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

  // -------------------------------------------------------------
  // 7. Drilldown Modal Dialog Logic & Keyboard Accessibility
  // -------------------------------------------------------------
  const modalBackdrop = document.getElementById('detailModal');
  const modalTitle = document.getElementById('modalTitle');
  const modalContent = document.getElementById('modalContent');
  const modalClose = document.getElementById('modalClose');
  let previouslyFocusedElement = null;

  const companyDetails = {
    CAMS: {
      title: "CAMS Limited — Investment Thesis & Audit Proof Points",
      body: `
        <div class="modal-detail-section" style="background: rgba(11, 18, 32, 0.5); padding: 16px; border-radius: 10px; border: 1px solid var(--border-accent);">
          <h4 style="color: var(--accent-bright); margin-bottom: 8px; font-weight: 700; font-size: 1rem;">Consensus Divergence & Moat</h4>
          <p style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.6;">
            CAMS commands a 68% AUM market share across Indian Mutual Funds with ~100% renewal rate and zero client defection in 15+ years. 
            At 29.6x trailing P/E and a 3.07% FCF yield, it requires only 34.9% 5Y FCFF CAGR to justify current price—the lowest hurdle in the coverage universe.
          </p>
        </div>
        <div class="modal-detail-section" style="background: rgba(11, 18, 32, 0.5); padding: 16px; border-radius: 10px; border: 1px solid var(--border-subtle); margin-top: 14px;">
          <h4 style="color: var(--text-primary); margin-bottom: 8px; font-weight: 700; font-size: 1rem;">Audit & Governance Assurance</h4>
          <p style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.6;">
            Audited by S.R. Batliboi (EY). Beneish M-Score of -1.92 completely passes financial manipulation screens. Zero leverage and FCF/PAT conversion exceeding 91.0%.
          </p>
        </div>
      `
    },
    CDSL: {
      title: "CDSL — Central Depository Services Audit Ledger",
      body: `
        <div class="modal-detail-section" style="background: rgba(11, 18, 32, 0.5); padding: 16px; border-radius: 10px; border: 1px solid var(--border-accent);">
          <h4 style="color: var(--accent-bright); margin-bottom: 8px; font-weight: 700; font-size: 1rem;">Beneficiary of Demat Account Penetration</h4>
          <p style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.6;">
            CDSL holds 66% market share in demat accounts. Annual issuer fees generate recurring non-market revenues, while capex intensity remains minimal at 2.5%.
          </p>
        </div>
        <div class="modal-detail-section" style="background: rgba(11, 18, 32, 0.5); padding: 16px; border-radius: 10px; border: 1px solid var(--border-subtle); margin-top: 14px;">
          <h4 style="color: var(--text-primary); margin-bottom: 8px; font-weight: 700; font-size: 1rem;">Key Forensic Monitorables</h4>
          <p style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.6;">
            Transaction fees remain cyclical with market turnover. M-Score is -1.77 (Investigate flag due to DSRI asset-growth surge), but audit is clean by Walker Chandiok.
          </p>
        </div>
      `
    },
    BSE: {
      title: "BSE Limited — Platform Moat vs Regulatory Risk",
      body: `
        <div class="modal-detail-section" style="background: rgba(11, 18, 32, 0.5); padding: 16px; border-radius: 10px; border: 1px solid var(--border-accent);">
          <h4 style="color: var(--warning); margin-bottom: 8px; font-weight: 700; font-size: 1rem;">Derivatives Hyper-Growth & Exposure</h4>
          <p style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.6;">
            Derivatives revenue has grown 15x over 4 years to 73.8% of total revenue. Trailing P/E of 55.1x requires an 81.1% reverse-DCF implied CAGR to justify price.
          </p>
        </div>
        <div class="modal-detail-section" style="background: rgba(11, 18, 32, 0.5); padding: 16px; border-radius: 10px; border: 1px solid var(--border-subtle); margin-top: 14px;">
          <h4 style="color: var(--text-primary); margin-bottom: 8px; font-weight: 700; font-size: 1rem;">Governance & Sizing Justification</h4>
          <p style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.6;">
            Deloitte audited. Capped at ₹66.5 Cr (13.3%) allocation with clear exit tripwires (TW1-TW3) safeguarding capital against severe SEBI volume curbs.
          </p>
        </div>
      `
    },
    KFIN: {
      title: "KFin Technologies — SaaS Platform & Global RTA",
      body: `
        <div class="modal-detail-section" style="background: rgba(11, 18, 32, 0.5); padding: 16px; border-radius: 10px; border: 1px solid var(--border-accent);">
          <h4 style="color: var(--accent-bright); margin-bottom: 8px; font-weight: 700; font-size: 1rem;">International Diversification</h4>
          <p style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.6;">
            Commands 32% domestic MF AUM plus major market shares in issuer solutions, pension, and international Southeast Asian RTA services.
          </p>
        </div>
        <div class="modal-detail-section" style="background: rgba(11, 18, 32, 0.5); padding: 16px; border-radius: 10px; border: 1px solid var(--border-subtle); margin-top: 14px;">
          <h4 style="color: var(--text-primary); margin-bottom: 8px; font-weight: 700; font-size: 1rem;">Forensic Highlights</h4>
          <p style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.6;">
            Composite score 100/100, Beneish M-Score of -2.02 (PASS), CFO/EBITDA 85.7%, FCF/PAT 113.6%. Audited by MSKA (BDO).
          </p>
        </div>
      `
    }
  };

  const openModal = (co) => {
    const details = companyDetails[co];
    if (details && modalBackdrop && modalTitle && modalContent) {
      previouslyFocusedElement = document.activeElement;
      modalTitle.textContent = details.title;
      modalContent.innerHTML = details.body;
      modalBackdrop.classList.add('open');
      modalBackdrop.setAttribute('aria-hidden', 'false');
      if (modalClose) modalClose.focus();
    }
  };

  const closeModal = () => {
    if (modalBackdrop) {
      modalBackdrop.classList.remove('open');
      modalBackdrop.setAttribute('aria-hidden', 'true');
      if (previouslyFocusedElement) {
        previouslyFocusedElement.focus();
      }
    }
  };

  document.querySelectorAll('.open-drilldown-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const co = btn.getAttribute('data-company');
      openModal(co);
    });
  });

  if (modalClose && modalBackdrop) {
    modalClose.addEventListener('click', closeModal);

    modalBackdrop.addEventListener('click', (e) => {
      if (e.target === modalBackdrop) {
        closeModal();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modalBackdrop.classList.contains('open')) {
        closeModal();
      }
    });
  }

  // -------------------------------------------------------------
  // 8. Number Count-up Animation for Headline Statistic
  // -------------------------------------------------------------
  const winStatEl = document.querySelector('.verdict-stat-pill .stat-number');
  if (winStatEl && !prefersReducedMotion()) {
    const targetVal = 96.4;
    let startVal = 0;
    const duration = 1200;
    const startTime = performance.now();

    const animateNumber = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const easedProgress = 1 - Math.pow(1 - progress, 3);
      const current = (startVal + (targetVal - startVal) * easedProgress).toFixed(1);
      winStatEl.textContent = `${current}%`;
      if (progress < 1) {
        requestAnimationFrame(animateNumber);
      } else {
        winStatEl.textContent = `${targetVal}%`;
      }
    };
    requestAnimationFrame(animateNumber);
  }
});
