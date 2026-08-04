FIX: DRILL-DOWN NOW RECONCILES EXACTLY TO THE CLICKED NUMBER
=============================================================
Cause: a vendor can appear in several GL groups (e.g. Gordon in Food COS
and other groups). The drill-down filtered by vendor + entity + month but
IGNORED the GL group of the clicked row - so it showed the vendor's
transactions across ALL groups and didn't tie to the cell.

Now the clicked row's GL group travels with the click:
  - Specific group selected: drill shows ONLY that group's line items and
    the total equals the clicked number to the penny
  - "ALL GROUPS" view: drill matches the merged number exactly
  - Row TOTAL and period comparisons reconcile the same way
  - The popup title now states the group so the scope is explicit

Proven numerically: Gordon Food Service LIB June - Food COS cell
$40,828.44 -> drill $40,828.44 (previously showed $46,319.36, the
cross-group total). Row TOTAL, ALL-mode, and prior-period comparison all
verified equal to the penny.

DEPLOY (backend + frontend):
  1. Downloads -> right-click drill_reconcile_fix.zip -> "Extract All..."
     -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 4 changed files -> "Commit to main" -> "Push origin"
  3. Backend changed: wait ~2 min; if drill totals still don't tie,
     railway.app -> AP_REC -> "web" box -> "Deployments" -> "..." ->
     "Redeploy". Then Ctrl+Shift+R.

Files:
  replaced AP_REC\backend\trends_engine.py
  replaced AP_REC\backend\main.py
  replaced AP_REC\frontend\src\pages\TrendsPage.jsx
  replaced AP_REC\frontend\src\components\DetailWindow.jsx
