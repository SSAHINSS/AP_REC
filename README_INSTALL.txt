ACCRUAL BUILDER: GL-ONLY VALIDATION
====================================
SUPERSEDES vendor_validation_fix.zip - do NOT upload that one; upload
only this.

Per your direction: the JE template defines the OUTPUT FORMAT ONLY.
All data validation - vendors, accounts, locations, the credit-account
picker - now comes exclusively from YOUR GL (a Sage export = the live
truth). The template's reference lists are no longer read at all.

  - Vendors: valid if they post in the GL with a V-#### Vendor ID
    (TradeCraft Origin validates; made-up names still blocked)
  - Accounts/locations: valid if they appear in the GL
  - Credit-account dropdown: 3xxxx liability accounts from the GL
  - Error messages now say "does not appear in your GL"
  - Self-maintaining: a fresh GL upload IS the refresh

(backend\sage_reference.json is now unused - harmless to leave, delete
whenever you like.)

DEPLOY (backend-only, 1 file):
  1. Downloads -> right-click gl_only_validation.zip -> "Extract All..."
     -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 1 changed file -> "Commit to main" -> "Push origin"
  3. Wait ~2 min for Railway; if behavior doesn't change:
     railway.app -> AP_REC -> "web" -> "Deployments" -> "..." ->
     "Redeploy". Then Ctrl+Shift+R; uncheck/recheck any flagged row to
     refresh its lookup.

Replaced file:
  AP_REC\backend\accrual_engine.py
