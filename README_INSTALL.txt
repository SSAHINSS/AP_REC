EXPENSE TRENDS v4: CARDHOLDER ANALYSIS + WINDOW READABILITY
===========================================================

WHAT CHANGED
  1. CREDIT CARDS BY CARDHOLDER — a new mode toggle at the top of the
     Expense Trends page: "Expense Trends" | "Credit Cards by Cardholder".
     The cardholder view shows CC spend ONLY (no AP), pivoted by
     cardholder x month, with:
       - Entity multi-select (one, several, or ALL)
       - Cardholder multi-select (one, several, or ALL - 76 detected)
       - Period range (from / to any month)
       - Every column sortable (cardholder, entities, txns, any month, total)
       - Click any amount -> the same floating window with that person's
         transactions (vendor, memo, doc, amount).
  2. POP-UP READABILITY — the drill-down window no longer truncates:
     long account/memo/cardholder/doc fields WRAP instead of cutting off,
     and hovering any cell shows the full value as a tooltip.
  3. BIGGER DEFAULT WINDOW — opens at 1180x680 (was 920x540).

HOW TO DEPLOY (every step):
  1. File Explorer -> Downloads -> right-click cardholder_analysis.zip ->
     "Extract All..." -> "Browse..." -> go to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract"
  2. Click "Yes" to merge folders, "Replace the files in the destination".
  3. Open GitHub Desktop -> 6 changed files (1 new: CardholderView.jsx) ->
     type a summary -> "Commit to main" -> "Push origin".
  4. Wait ~2 min. Backend changed: if the cardholder view errors after
     deploy, railway.app -> AP_REC -> "web" box -> "Deployments" ->
     "..." on the newest -> "Redeploy".

Files:
  NEW      AP_REC\frontend\src\pages\CardholderView.jsx
  replaced AP_REC\backend\trends_engine.py
  replaced AP_REC\backend\main.py
  replaced AP_REC\frontend\src\api.js
  replaced AP_REC\frontend\src\pages\TrendsPage.jsx
  replaced AP_REC\frontend\src\components\DetailWindow.jsx
