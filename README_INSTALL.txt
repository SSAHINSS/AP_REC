NEW MODULE: ACCRUAL BUILDER (EXPERIMENTAL)
===========================================
Review AP spend like Expense Trends, check the vendors to accrue, enter
amounts, export ONE Sage-ready JE import CSV per entity.

THE WORKFLOW (numbered steps in the UI):
  1. Pick entity + close month (JEs are per entity)
  2. Pick the accrual (credit) account - REMEMBERED from your last use
  3. Check vendors to accrue. Amounts start BLANK by design. Account +
     location prefill from that vendor's GL history (editable). CC lines
     can't be accrued (already paid). Click any month number to open the
     reconciled drill-down. Everything AUTOSAVES per entity+month - you
     can stop and resume tomorrow.
  4. Export JE CSV - one balanced entry: a debit line per vendor (with
     Sage vendor ID), one credit to your accrual account, DATE =
     month-end, REVERSEDATE = 1st of next month (Sage auto-reverses),
     REFERENCE ACCR-<ENTITY>-<YYYYMM>.

"TRICKY AND PICKY" INSURANCE:
  Your template's hidden reference sheets (631 accounts / 59 locations /
  1,531 vendors) are baked in as the validation authority. Every line is
  checked BEFORE the file is created - a bad account, location, vendor
  name, or amount BLOCKS the export and lists exactly what to fix. If
  the export downloads, it imports. Verified: exact 41-column header
  match, MM/DD/YYYY dates, balanced debits/credits, sequential line
  numbers, vendor IDs populated.

NOTES:
  - Uses the same GL as Expense Trends (one upload feeds both)
  - Expense Trends is UNTOUCHED, per your "not yet" - this runs alongside
  - NEW PERMISSION: "Accruals" - existing non-admin users DON'T have it
    until you grant it in Users (admins see it automatically)

DEPLOY (backend + frontend):
  1. Downloads -> right-click accrual_builder.zip -> "Extract All..." ->
     "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 9 changed files (3 new) -> "Commit to main" ->
     "Push origin"
  3. Backend changed: wait ~2 min; if the module errors on load,
     railway.app -> AP_REC -> "web" box -> "Deployments" -> "..." ->
     "Redeploy". Then Ctrl+Shift+R.

ACCEPTANCE TEST once live: LIB + June -> credit acct 30100 Accrued
Expenses -> check Gordon Food Service -> enter an amount -> Export ->
open the CSV: line 1 debits 60100/LIB-96100 with V-0584, line 2 credits
30100, dates 06/30/2026 rev 07/01/2026.

Files:
  NEW      AP_REC\backend\accrual_engine.py
  NEW      AP_REC\backend\sage_reference.json
  NEW      AP_REC\frontend\src\pages\AccrualPage.jsx
  replaced AP_REC\backend\db.py
  replaced AP_REC\backend\main.py
  replaced AP_REC\frontend\src\api.js
  replaced AP_REC\frontend\src\App.jsx
  replaced AP_REC\frontend\src\components\Sidebar.jsx
  replaced AP_REC\frontend\src\pages\HomePage.jsx
