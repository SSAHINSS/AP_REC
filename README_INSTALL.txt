ACCRUAL BUILDER: CC TRANSACTIONS REMOVED
=========================================
Credit-card vendor rows no longer appear in the Accrual Builder at all -
they were unactionable clutter (already paid, nothing to accrue).
Groups whose vendors were all credit-card disappear with them. MIX rows
(vendors with both AP and CC activity) remain, since their AP side is
accruable. Expense Trends still shows everything, including CC.

DEPLOY (Netlify-only, 1 file):
  1. Downloads -> right-click accrual_no_cc.zip -> "Extract All..." ->
     "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 1 changed file -> "Commit to main" -> "Push origin"
  3. ~1 min, then Ctrl+Shift+R.

Replaced file:
  AP_REC\frontend\src\pages\AccrualPage.jsx
