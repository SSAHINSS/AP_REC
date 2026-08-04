ACCRUAL BUILDER: COMMAS + DROPDOWN BACK + MICROCOPY PURGE
==========================================================
1. Amounts format with thousands separators when committed (Enter or
   leaving the field): 41000 -> 41,000. Commas are understood on
   re-edit and inside quick math ("41,000+500" -> 41,500).
2. The accrual account DROPDOWN is back and always populated: 3xxxx
   accounts from the GL when the export contains them, otherwise the
   standard accrual accounts (30100 Accrued Expenses, 30200 AP, 35600
   Accrued Wages, 35700 Accrued Taxes, 401k/WC/Health payables), plus
   "Other..." which reveals a compact 5-digit account box.
3. Removed: the experimental banner paragraph, the "one entity at a
   time" note, the "5-digit accrual account..." explanation, and the
   whole step-3 instruction block. The empty-state prompt is now just
   "Select an entity to begin."

DEPLOY (backend + frontend, 2 files):
  1. Downloads -> right-click accrual_ui_pass.zip -> "Extract All..."
     -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 2 changed files -> "Commit to main" -> "Push origin"
  3. Backend changed: wait ~2 min; if the dropdown is empty,
     railway.app -> AP_REC -> "web" -> "Deployments" -> "..." ->
     "Redeploy". Then Ctrl+Shift+R.

Files:
  replaced AP_REC\backend\accrual_engine.py
  replaced AP_REC\frontend\src\pages\AccrualPage.jsx
