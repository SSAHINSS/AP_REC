FIX: STALE "NOT IN SAGE" WARNING + PLACEHOLDER CLEANUP
=======================================================
1. TRADECRAFT (and any row flagged before the validation fix): the
   warning verdict was CACHED in your saved draft, and re-checking a row
   reused the cache instead of asking the backend again - so no backend
   fix could reach it. Now: every time a row is checked it re-validates
   fresh, and saved drafts re-validate all checked rows on load. Stale
   verdicts cannot survive.
2. The amount field placeholder is just "0.00" again. The quick-math
   capability (40*4 -> 160) still works - it's explained in the hint
   line and the field tooltip, not shouted from the placeholder.

IMPORTANT: this fix works ONLY if the backend from gl_only_validation
is actually live. Verify: railway.app -> AP_REC -> "web" ->
"Deployments" -> newest shows green "Success" AFTER your
gl_only_validation push. If unsure: "..." -> "Redeploy". A stale
backend keeps producing the old verdicts no matter what the frontend
does.

DEPLOY (Netlify-only, 1 file):
  1. Downloads -> right-click accrual_revalidate.zip -> "Extract All..."
     -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 1 changed file -> "Commit to main" -> "Push origin"
  3. ~1 min, Ctrl+Shift+R, reopen the entity - TradeCraft's flag clears
     on load (or on next check).

Replaced file:
  AP_REC\frontend\src\pages\AccrualPage.jsx
