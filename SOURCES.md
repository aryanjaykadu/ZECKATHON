# Data Sources Registry

This document records all data sources utilized for the equity research project on Indian capital-markets infrastructure companies (BSE Ltd, CDSL, CAMS, KFin Technologies).

## 1. Primary Sources (Official & Regulatory)

| Source Name | Organization / Entity | Portal URL | Data Acquired | Verification & Attribution |
|-------------|----------------------|------------|---------------|----------------------------|
| **NSE Corporate Announcements API & Archives** | National Stock Exchange of India (NSE) | `https://www.nseindia.com/api/corporate-announcements` & `https://nsearchives.nseindia.com/corporate/` | • Quarterly Financial Results (PDF, last 8 quarters for BSE, CDSL, CAMS, KFINTECH)<br>• Investor Presentations (PDF, last 8 quarters)<br>• Earnings Call Transcripts (PDF, last 8 quarters) | Verified against exchange dissemination timestamps (`dt`), SHA256 checksums, and official NSE broadcast intimations. |
| **NSE Shareholding Master API** | National Stock Exchange of India (NSE) | `https://www.nseindia.com/api/corporate-share-holdings-master` & `https://nsearchives.nseindia.com/corporate/xbrl/` | • Quarterly Shareholding Patterns (XBRL/XML, last 8 quarters for BSE, CDSL, CAMS, KFINTECH) | Verified against SEBI Reg 31 filing dates, official XML schemas, and submission timestamps. |
| **NSE Annual Reports Archives** | National Stock Exchange of India (NSE) | `https://www.nseindia.com/api/annual-reports` & `https://nsearchives.nseindia.com/annual_reports/` | • Annual Reports for BSE Ltd, CAMS, KFin Technologies (FY21-22 to FY25-26) | Extracted from official listed entity repository. |
| **CDSL Investor Relations Portal** | Central Depository Services (India) Ltd | `https://www.cdslindia.com/InvestorRels/AnnualReports.html` | • CDSL Integrated Annual Reports (FY20-21 through FY25-26) | Direct download from CDSL corporate servers. |
| **SEBI Regulatory Circulars & Compliance Directives** | Securities and Exchange Board of India (SEBI) / NSE / BSE | `https://nsearchives.nseindia.com/content/circulars/` & `https://www.bseindia.com/markets/MarketInfo/` | • **True to Label MII Charges**: Circular `NSE/FA/64232` (implementing `SEBI/HO/MRD/TPD-1/P/CIR/2024/92`)<br>• **Weekly Index Expiry Rationalization**: Circular `NSE/FAOP/64506` (implementing `SEBI/HO/MRD/TPD-1/P/CIR/2024/132`)<br>• **Index Contract Lot Size Revision**: Circular `NSE/FAOP/70616`<br>• **BSE BANKEX Lot Size Revision**: BSE Notice `20241021-13` | Regulatory notices issued directly to clearing corporations, exchanges, and depositories. |
| **SEBI Monthly Bulletin & Statistics** | Securities and Exchange Board of India (SEBI) - DEPA | `https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=4&ssid=80&smid=107` | • **Secondary Market Derivatives Turnover**: Monthly NSE + BSE futures & options turnover across contracts<br>• **Depository Demat Accounts**: Monthly CDSL & NSDL cumulative beneficiary accounts & monthly additions (Annexure Tables) | Official statistical tables published by SEBI Department of Economic and Policy Analysis. |
| **AMFI India Research Data Portal** | Association of Mutual Funds in India (AMFI) | `https://www.amfiindia.com/research-information/amfi-monthly` | • Monthly mutual fund AUM, average AUM, sales, redemptions, net inflows, and granular folio counts across schemes (60 monthly Excel workbooks covering 5 fiscal years: Oct 2021 – Sep 2026) | Directly sourced from `https://portal.amfiindia.com/spages/`. |
| **RBI Handbook of Statistics on the Indian Economy** | Reserve Bank of India (RBI) | `https://www.rbi.org.in/scripts/AnnualPublications.aspx?head=Handbook+of+Statistics+on+Indian+Economy` | • **Table 40**: Major Monetary Policy Rates (Policy Repo Rate, Reverse Repo, SDF, MSF, Bank Rate, CRR, SLR historical series)<br>• **Table 178**: Government Dated Securities Yields across maturities (10-year G-sec benchmark yield) | Official macro time-series workbooks published by the Reserve Bank of India. |

## 2. Secondary Sources (Cross-Check & Price Data)

| Source Name | Platform | Tickers / Symbols | Data Acquired | Notes & Justification |
|-------------|----------|-------------------|---------------|------------------------|
| **Yahoo Finance (yfinance)** | Yahoo Finance API | `BSE.NS`, `CDSL.NS`, `CAMS.NS`, `KFINTECH.NS`, `^NSEI` | Daily OHLCV data from inception / 2016-10-27 through 2026-10-26 (cutoff date enforced) | Secondary cross-check for split/bonus adjusted daily market pricing. All records verified strictly `<= 2026-10-26`. |

## 3. Compliance and Verification Notes
- **Cutoff Date**: All data acquired strictly reflects publications and market periods on or prior to **2026-10-26**.
- **Integrity**: Every downloaded file has an entry in `data/download_log.csv` containing source URL, publication timestamp, access date, file size, notes, and SHA-256 hash.
