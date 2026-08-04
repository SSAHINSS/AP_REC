ACCRUAL AMOUNT FIELD: CALCULATOR INPUT
=======================================
Type math straight into the amount field:
  40*4          -> 160
  (1200+80)/2   -> 640
  1,200.50+80   -> 1280.50   ($ and commas are fine)
Enter computes it in place; leaving the field computes it too. Digits
and + - * / ( ) only - anything else is ignored as not-a-number, and
the export/total always use the COMPUTED value even if you never press
Enter (an uncommitted "40*4" can no longer sneak into a JE as 40).

DEPLOY (Netlify-only, 1 file):
  1. Downloads -> right-click accrual_calc_input.zip -> "Extract All..."
     -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 1 changed file -> "Commit to main" -> "Push origin"
  3. ~1 min, then Ctrl+Shift+R.

Replaced file:
  AP_REC\frontend\src\pages\AccrualPage.jsx
