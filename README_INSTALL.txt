GL ARCHITECTURE: PER-MODULE GL SOURCE + SIDEBAR ORDER + HOME CLEANUP
=====================================================================

USER ISOLATION (your requirement, verified by test):
  Every GL is stored per-account. User A's uploads are INVISIBLE to
  user B - proven: A uploads, B's status shows nothing and B's modules
  refuse to run until B uploads their own.

WHAT CHANGED
  1. GL lives on the MODULES now, not Home. AP Rec, Expense Trends and
     Payroll each have a "GL Source" bar at the top showing exactly
     which file that module will use.
  2. SHARED BY DEFAULT, OVERRIDE WHEN NEEDED: all modules read your
     shared GL (upload once, use everywhere). Any module can switch to
     its own file: "Use different GL for <module> only" - and "Revert
     to shared GL" undoes it. The bar always states which is active.
  3. AP REC: attaching a GL per run is now OPTIONAL - leave it empty
     and it uses your saved GL. Attaching one also saves it as your
     AP-Rec-specific GL for next time.
  4. SIDEBAR ORDER: Home, AP Rec, Expense Trends, Payroll, File Namer.
  5. HOME: pure module launcher - no GL dropzone, no locks.

DEPLOY (backend + frontend):
  1. Downloads -> right-click gl_architecture.zip -> "Extract All..."
     -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 9 changed files (1 new: GlPicker.jsx) ->
     "Commit to main" -> "Push origin".
  3. Backend changed: wait ~2 min; if the GL Source bar errors,
     railway.app -> AP_REC -> "web" box -> "Deployments" -> "..." ->
     "Redeploy". Then Ctrl+Shift+R.

  The database migrates itself safely (adds the scope column; existing
  saved GLs become the "shared" slot - nothing is lost).

Files:
  NEW      AP_REC\frontend\src\components\GlPicker.jsx
  replaced AP_REC\backend\db.py
  replaced AP_REC\backend\main.py
  replaced AP_REC\frontend\src\api.js
  replaced AP_REC\frontend\src\components\Sidebar.jsx
  replaced AP_REC\frontend\src\pages\HomePage.jsx
  replaced AP_REC\frontend\src\pages\TrendsPage.jsx
  replaced AP_REC\frontend\src\pages\PayrollPage.jsx
  replaced AP_REC\frontend\src\pages\AppPage.jsx
