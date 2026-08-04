FIX: ACCRUAL ACCOUNT SELECTOR EMPTY
====================================
Root cause (measured): your live GL export is expense-focused and
contains ZERO 3xxxx liability accounts - so under GL-only validation
the credit dropdown had nothing to list. (It only "worked" earlier
because choices came from the template list we removed.)

Fix - the credit account is the controller's deliberate choice, the one
field the GL legitimately can't testify about:
  - GL has 3xxxx accounts -> dropdown (as before), and a remembered
    account not in the list still shows as "(remembered)"
  - GL has none -> a strict 5-digit account input with an explanation,
    remembered exactly like the dropdown selection
  - Export requires a well-formed 5-digit credit account; per-row debit
    accounts/locations remain GL-derived and GL-validated as before

Verified on both GL shapes: newer export -> input mode, typed 30100
exports a balanced JE; malformed "301" is blocked; older full export ->
50-account dropdown.

DEPLOY (backend + frontend, 2 files):
  1. Downloads -> right-click credit_selector_fix.zip -> "Extract All..."
     -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 2 changed files -> "Commit to main" -> "Push origin"
  3. Backend changed: wait ~2 min; if the selector is still empty,
     railway.app -> AP_REC -> "web" -> "Deployments" -> "..." ->
     "Redeploy". Then Ctrl+Shift+R.

Files:
  replaced AP_REC\backend\accrual_engine.py
  replaced AP_REC\frontend\src\pages\AccrualPage.jsx
