REVERT: AP REC BACK TO THE SIMPLE TWO-STEP FLOW
================================================
The GL Source bar is removed from AP Rec. The module is exactly as it
was: 01 - drop the GL, 02 - drop the statements, Run. One dropzone for
each thing, GL required per run.

Expense Trends and Payroll keep their GL Source bars (those modules
have no per-run upload, so the bar is their only GL control).

DEPLOY (Netlify-only, 1 file):
  1. Downloads -> right-click aprec_revert.zip -> "Extract All..." ->
     "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 1 changed file -> "Commit to main" -> "Push origin"
  3. ~1 min, then Ctrl+Shift+R.

Replaced file:
  AP_REC\frontend\src\pages\AppPage.jsx
