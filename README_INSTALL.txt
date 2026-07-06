ANALYZE PAGE — INSTALL (no file editing needed)
===============================================
Adds a 4th page, "Analyze": upload the Sage Intacct GL CSV and it flags
missing bills, spikes, trailing-off vendors, and duplicate invoices across
the trailing 12 months. GL only — no Bill.com yet.

1. Extract this zip into the AP_REC repo folder:
   C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC

2. Windows: merge folders -> YES; replace files -> REPLACE ALL.
   New files : backend\flag_engine.py, frontend\src\pages\AnalyzePage.jsx
   Replaced  : backend\main.py, frontend\src\api.js,
               frontend\src\App.jsx, frontend\src\components\Sidebar.jsx

3. GitHub Desktop -> commit -> push. Railway (backend) + Netlify (frontend)
   auto-deploy. If /flags/analyze 404s after deploy, redeploy latest on
   Railway to clear the Docker cache.

4. Delete this README before committing (optional).
