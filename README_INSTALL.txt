FIX: "duplicate key ... ix_gl_files_user_id" WHEN RECONCILING
==============================================================
(Silver lining: this error means POSTGRES IS LIVE - data now persists.)

Cause: the old one-GL-per-user database rule existed as a unique INDEX
(ix_gl_files_user_id); the scope migration only removed it under its
CONSTRAINT name, so attaching a GL (which stores a second, AP-Rec-scoped
row) hit the leftover rule and failed.

Fix: the migration now removes the rule under BOTH names, restores a
plain lookup index, and keeps the correct per-(user, scope) rule.
Runs automatically at boot; safe to re-run; no data is touched.
Reproduced the exact failure and verified it now succeeds.

DEPLOY (backend-only, 1 file):
  1. Downloads -> right-click gl_migration_fix.zip -> "Extract All..."
     -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 1 changed file -> "Commit to main" -> "Push origin"
  3. Wait ~2 min for Railway. If the same error appears after that:
     railway.app -> AP_REC -> "web" box -> "Deployments" -> "..." ->
     "Redeploy" (the fix runs at boot, so a fresh boot is required).
  4. Have the user retry their reconciliation - no other action needed.

Replaced file:
  AP_REC\backend\db.py
