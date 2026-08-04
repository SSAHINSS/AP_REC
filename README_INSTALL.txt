ACCRUAL BUILDER POLISH - all five items
========================================
SUPERSEDES accrual_warning_fix.zip - do NOT upload that one; everything
in it is included here.

1. HEADER: real ACCRUALS pixel logo built from the same canonical glyph
   library as every other module (identical A/C/R/L/S glyphs; U derived
   from the canonical O), same rain animation, same hover, with the
   "Accrual Builder / experimental" subtitle.
2. (BLANK) VENDORS: rows stay visible for context but show "no vendor"
   instead of a checkbox - there is no Sage vendor to accrue against.
3. NO FREE-FOR-ALL: the debit ACCOUNT and LOCATION are no longer typed.
   They are set automatically from the vendor's posting history in the
   SELECTED ENTITY and shown read-only as "-> 60100 @ LIB-96100".
   Entity is a single labeled dropdown - one entity at a time, stated
   right on the screen.
4/5. INTUITIVE: the accrue column header says what to do ("ACCRUE -
   CHECK & ENTER $"), the amount field is $-labeled and auto-focuses on
   check, lookups show "looking up acct/location...", the Sage-vendor
   warning is a readable chip, and the step hint explains the whole flow
   in one line.

DEPLOY (Netlify-only, 3 files - 1 new):
  1. Downloads -> right-click accrual_polish.zip -> "Extract All..." ->
     "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 3 changed files -> "Commit to main" -> "Push origin"
  3. ~1 min, then Ctrl+Shift+R.

Files:
  NEW      AP_REC\frontend\src\components\AccrualLogo.jsx
  replaced AP_REC\frontend\src\App.jsx
  replaced AP_REC\frontend\src\pages\AccrualPage.jsx
