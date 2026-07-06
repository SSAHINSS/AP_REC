FIX: remove the duplicate "Analyze" page + add animated TRENDS logo
===================================================================

STEP 1 — DELETE these two files from your repo (File Explorer):
  C:\...\AP_REC\backend\flag_engine.py
  C:\...\AP_REC\frontend\src\pages\AnalyzePage.jsx

STEP 2 — Extract this zip into:
  C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
  Merge folders: YES.  Replace files: REPLACE ALL.

STEP 3 — GitHub Desktop should show:
  modified: backend/main.py
  modified: frontend/src/api.js
  modified: frontend/src/App.jsx
  modified: frontend/src/components/Sidebar.jsx
  new:      frontend/src/components/TrendsLogo.jsx
  deleted:  backend/flag_engine.py
  deleted:  frontend/src/pages/AnalyzePage.jsx
  Commit -> Push. Railway + Netlify auto-deploy.

Result: sidebar back to 3 pages (AP Rec, File Namer, Trends).
Trends page opens with the animated TRENDS logo matching the others.
