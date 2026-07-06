EXPENSE TRENDS v2: CREDIT CARDS + DRILL-DOWN + OPS EXCEL REPORT
===============================================================

WHAT CHANGED
  1. RENAMED to Expense Trends (new pixel logo + sidebar label).
  2. CREDIT-CARD SPEND NOW HAS REAL VENDORS. CC lines (CRJ journal) carry
     "Vendor | Cardholder | ... " in the Document description field.
     The vendor is extracted automatically - 5,786 transactions worth
     $913K stop hiding under "(blank)". Cardholder + memo are kept and
     shown in drill-downs with a credit-card chip.
  3. DRILL-DOWN: click any month amount OR any row TOTAL to see the
     transactions behind it - date, location, account, cardholder, memo,
     doc #, amount - in a clean readable panel (not a raw pivot dump).
  4. EXPORT REPORT (xlsx) button: builds a styled workbook for ops -
     vendor x month grid sectioned by GL group (orange headers, dark
     group bands with live SUM formulas, flagged rows tinted amber/red,
     analysis month highlighted) + a Review Queue sheet of all flags.
     Sample included: EXPENSE_TRENDS_LIB_2026-06.xlsx (verified: 673
     live formulas, zero errors).

HOW TO DEPLOY (every step):
  1. File Explorer -> Downloads -> right-click expense_trends_v2.zip ->
     "Extract All..." -> "Browse..." -> go to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract"
  2. Click "Yes" to merge folders, "Replace the files in the destination".
  3. Open GitHub Desktop -> 8 changed files (1 new: trends_report.py) ->
     type a summary -> "Commit to main" -> "Push origin".
  4. Wait ~2 min. Backend changed: if CC vendors don't appear after
     deploy, railway.app -> AP_REC -> "web" box -> "Deployments" ->
     "..." on newest -> "Redeploy".

Files:
  NEW      AP_REC\backend\trends_report.py
  replaced AP_REC\backend\trends_engine.py
  replaced AP_REC\backend\main.py
  replaced AP_REC\frontend\src\api.js
  replaced AP_REC\frontend\src\App.jsx
  replaced AP_REC\frontend\src\pages\TrendsPage.jsx
  replaced AP_REC\frontend\src\components\TrendsLogo.jsx
  replaced AP_REC\frontend\src\components\Sidebar.jsx
