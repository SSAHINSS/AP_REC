FIX: TRENDS + PAYROLL logo size now matches AP-REC / FILE-NMR
=============================================================
The two newer logos had a shorter SVG viewBox (142 vs 158) and too-small
render widths, so their letters drew ~15-20% smaller. Now normalized to
the same letter height as FILE-NMR.

Extract this zip into:
  C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
Merge folders: YES.  Replace files: REPLACE ALL.

Replaced files:
  AP_REC\frontend\src\App.jsx
  AP_REC\frontend\src\components\TrendsLogo.jsx
  AP_REC\frontend\src\components\PayrollLogo.jsx

GitHub Desktop: commit -> push. Netlify-only (no Railway change).
