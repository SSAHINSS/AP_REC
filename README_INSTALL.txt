WAVE 2: PAYROLL MODULE (accrual calculator + payroll trends)
============================================================
Requires wave 1 deployed (it is — commit qahjte).

WHAT THIS ADDS
  New "Payroll" page in the sidebar with the animated PAYROLL logo:
  1. MONTH-END ACCRUAL CALCULATOR
     - Auto-detects each entity's pay schedule from the GL
       (SH/OE/RRT/PRED/MAD/LIB/ODS/OCMGT = biweekly cohort 1,
        JTS = biweekly cohort 2, WRI = weekly, CRP = pick manually)
     - Pay periods Mon-Sun, check = period end + 5 days (your schedule images)
     - Days to accrue computed per entity per month
       (June 2026: cohort 1 = 9 days, cohort 2 = 16 days - validated)
     - Daily rate per category from actual PYRJ pay runs; math shown
     - Categories: Hourly, Salaried, Payroll Taxes, Labor COS,
       Benefits (401k/dental/admin), Contract/Temp
     - Grand total + per-entity totals + reversal date (1st of next month)
     - Schedule override dropdown per entity
  2. PAYROLL TRENDS
     - Category x trailing 12 months + YTD avg/mo + LY YTD avg + delta %
     - Uses the SAME saved GL as the Trends page (no re-upload)

STEP 1 — (if you haven't already) DELETE this leftover file:
  AP_REC\backend\trends_api.py

STEP 2 — Extract this zip into:
  C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
  Merge folders: YES.  Replace files: REPLACE ALL.

  New files:
    AP_REC\backend\payroll_engine.py
    AP_REC\frontend\src\components\PayrollLogo.jsx
    AP_REC\frontend\src\pages\PayrollPage.jsx
  Replaced files:
    AP_REC\backend\main.py
    AP_REC\frontend\src\api.js
    AP_REC\frontend\src\App.jsx
    AP_REC\frontend\src\components\Sidebar.jsx

STEP 3 — GitHub Desktop: commit -> push. Railway + Netlify auto-deploy.
  If /payroll/* 404s after deploy: Railway -> Deployments -> Redeploy latest.

NOTES
  - JE export (Intacct import file) is intentionally NOT built yet (your call).
    When ready, I need: (a) a GL export that includes 2xxxx liability accounts
    (this one is filtered to P&L), or just the accrued-payroll account number(s);
    (b) a past Intacct JE import file as the template.
  - LY YTD column shows "-" until you load a GL covering last year (18-24 mo).
