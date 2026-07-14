EXPENSE TRENDS v3: CC/AP INDICATOR + FLOATING DRILL-DOWN + UNIVERSAL SORT
=========================================================================

WHAT CHANGED
  1. CC vs AP in the same table: a new sortable TYPE column tags each
     vendor row - 💳 CC, AP, or ◐ MIX (paid both ways; hover shows the
     CC/AP split). One holistic table, but you can tell payment method at
     a glance and sort by it (click the TYPE header).
  2. FLOATING DRILL-DOWN WINDOW: clicking any number opens a draggable
     window (move it by the title bar, resize from the bottom-right corner,
     minimize (-), maximize (window icon), close (X)). It floats over the
     page - no lost scroll position, no new browser tab.
  3. COMPARE UP TO 3 PERIODS: inside the window, "Compare to" buttons -
     Prior period, Same month last year, Two periods prior - show the
     transaction detail side by side.
  4. EVERY TABLE SORTABLE: click any header in the drill-down window
     (date, location, type, account, cardholder, memo, doc #, amount) to
     sort asc/desc. The main table's every column is sortable too.

HOW TO DEPLOY (every step):
  1. File Explorer -> Downloads -> right-click expense_trends_v3.zip ->
     "Extract All..." -> "Browse..." -> go to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract"
  2. Click "Yes" to merge folders, "Replace the files in the destination".
  3. Open GitHub Desktop -> 6 changed files (2 new: DetailWindow.jsx,
     useSort.js) -> type a summary -> "Commit to main" -> "Push origin".
  4. Wait ~2 min. Backend changed: if comparisons error after deploy,
     railway.app -> AP_REC -> "web" box -> "Deployments" -> "..." on the
     newest -> "Redeploy".

Files:
  NEW      AP_REC\frontend\src\components\DetailWindow.jsx
  NEW      AP_REC\frontend\src\components\useSort.js
  replaced AP_REC\backend\trends_engine.py
  replaced AP_REC\backend\main.py
  replaced AP_REC\frontend\src\api.js
  replaced AP_REC\frontend\src\pages\TrendsPage.jsx
