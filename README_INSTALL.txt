PAYROLL v2: PYRJ-ONLY MATH + DRILL-DOWN + ALREADY-ACCRUED WARNINGS
==================================================================

THE MATH (your rule, now enforced with zero exceptions):
  Daily rates are computed from PYRJ (Payroll Journal) postings ONLY.
  GJ/IJ adjusting entries, accruals, reversals, and transfers can never
  touch the rate. Entities with no PYRJ activity (RRT, CRP, CSC, HBP)
  show an explicit "cannot compute" note instead of a polluted estimate.

NEW FEATURES:
  1. ALREADY-ACCRUED WARNING (warn only - the math never changes):
     each entity is scanned for payroll accruals already posted in the
     close month (credits to 35600/35700/30201/30205/30206, classified
     so standing bonus/401k/property-tax accruals don't false-alarm).
     A yellow banner shows date, account, amount, description, doc #.
  2. RATE DRILL-DOWN: click any category row in the calculator to see
     every PYRJ posting that built the rate, plus an expandable list of
     everything EXCLUDED and why.
  3. TRENDS DRILL-DOWN: click any amount in Payroll Trends to see the
     GL lines behind that cell.

HOW TO DEPLOY (every step):
  1. File Explorer -> Downloads -> right-click payroll_v2_pyrj_drilldown.zip
     -> "Extract All..." -> "Browse..." -> go to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract"
  2. Click "Yes" to merge folders, "Replace the files in the destination".
  3. Open GitHub Desktop -> 4 changed files appear -> type a summary ->
     "Commit to main" -> "Push origin".
  4. Wait ~2 min. Backend changed: if the Payroll page shows no warnings
     after deploy, go to railway.app -> AP_REC project -> click the "web"
     box -> "Deployments" tab -> "..." on the newest -> "Redeploy".

Replaced files:
  AP_REC\backend\payroll_engine.py
  AP_REC\backend\main.py
  AP_REC\frontend\src\api.js
  AP_REC\frontend\src\pages\PayrollPage.jsx
