WAVE 3: HOME PAGE (single GL upload) + LIGHT-THEME CONTRAST FIX
===============================================================

WHAT THIS ADDS
  1. NEW "HOME" PAGE — first item in the sidebar, and the landing page.
     One upload spot for the GL that drives Trends AND Payroll.
     Shows what's on file (name, dates, rows, entities) and module tiles.
     - Trends no longer has its own upload; it reads the saved GL.
     - Payroll unchanged in behavior; its "no GL" message points to Home.
  2. LIGHT THEME CONTRAST — status colors (flag chips, warnings, errors,
     ok/green, row stripes) are now theme-aware: bright pastels on dark,
     deeper readable tones on the off-white background.
  3. Full-GL support — the two new sales accounts in the complete GL
     export are mapped; balance-sheet accounts are excluded as before.

STEP 1 — Extract this zip into:
  C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
  Merge folders: YES.  Replace files: REPLACE ALL.

  New files:
    AP_REC\frontend\src\pages\HomePage.jsx
    AP_REC\frontend\src\components\HomeLogo.jsx
  Replaced files:
    AP_REC\backend\main.py
    AP_REC\backend\trends_engine.py
    AP_REC\frontend\src\api.js
    AP_REC\frontend\src\App.jsx
    AP_REC\frontend\src\index.css
    AP_REC\frontend\src\components\Sidebar.jsx
    AP_REC\frontend\src\pages\TrendsPage.jsx
    AP_REC\frontend\src\pages\PayrollPage.jsx

STEP 2 — GitHub Desktop: commit -> push. Railway + Netlify auto-deploy.
  If /gl/upload 404s after deploy: Railway -> Deployments -> Redeploy latest.

STEP 3 — Sign in, land on Home, drop csvdownload (25).csv (the full GL),
  then open Trends or Payroll — both feed off it automatically.

FOUND IN YOUR FULL GL (for the future JE export):
  Accrued payroll credit account = 35600 Accrued Wages (by entity),
  35700 Accrued Taxes. Also 30201 Accrued 401k / 30205 Workers Comp /
  30206 Health Ins. JE export stays on hold per your call.
