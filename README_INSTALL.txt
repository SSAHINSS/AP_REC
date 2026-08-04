FIX: ACCRUAL BUILDER NOT VISIBLE
=================================
Cause: the frontend permission helper hardcoded the module list and was
never taught about the new module - so the sidebar and Home filtered
Accrual Builder out even for admins. One-file fix.

DEPLOY (Netlify-only, 1 file):
  1. Downloads -> right-click accruals_visible_fix.zip -> "Extract All..."
     -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 1 changed file -> "Commit to main" -> "Push origin"
  3. ~1 min, then Ctrl+Shift+R. The Accrual Builder icon appears at the
     bottom of the sidebar + a tile on Home.

Non-admin users still need the "Accruals" permission granted in Users
(and to sign out/in once after you grant it).

Replaced file:
  AP_REC\frontend\src\api.js
