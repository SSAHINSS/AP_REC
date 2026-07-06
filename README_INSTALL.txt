AP TRENDS UPDATE: 13-month window, one table + GL dropdown,
click-to-sort headers, smart default month, renamed page
===========================================================

WHAT CHANGED
  1. Window = analysis month + the 12 before it (June '26 -> June '25).
     Your current GL starts Aug '25, so it shows what exists; pull a
     longer export and the extra columns appear automatically.
  2. Page renamed AP TRENDS (new pixel logo + sidebar label).
  3. ONE table. The per-group sections are gone; a "GL Group" dropdown
     (P&L order, plus ALL GROUPS) filters the same table in place.
  4. Click any month header, TOTAL, or VENDOR to sort. First click =
     high-to-low, click again = low-to-high. Arrow shows the active sort.
  5. Default Analysis Month: through the 10th of a month it defaults to
     the PRIOR month (until Jul 10 2026 -> June 2026), then the current.

Extract this zip into:
  C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
Merge folders: YES.  Replace files: REPLACE ALL.

Replaced files:
  AP_REC\backend\trends_engine.py
  AP_REC\frontend\src\pages\TrendsPage.jsx
  AP_REC\frontend\src\components\TrendsLogo.jsx
  AP_REC\frontend\src\components\Sidebar.jsx
  AP_REC\frontend\src\App.jsx

GitHub Desktop: commit -> push. Railway + Netlify auto-deploy.
(Backend changed too — if results look stale, Redeploy latest on Railway.)
