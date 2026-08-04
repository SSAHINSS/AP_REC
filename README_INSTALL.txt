FIX: JE EXPORT FILENAME - ENTITY + DATES, ALWAYS UNIQUE
========================================================
Downloads are now named like:
  JE_Import_LIB_2026-06_exported_2026-08-04_1532.csv
i.e. entity + close month + the exact date/time of export - so two
exports of the same entity/month never collide, and the file identifies
itself in a folder full of month-end uploads.

(Why it was generic before: the server-side filename travels in a
response header that browsers hide from cross-origin JavaScript, so the
download fell back to a default. The name is now built in the app from
the entity and period you selected.)

DEPLOY (Netlify-only, 1 file):
  1. Downloads -> right-click je_filename_fix.zip -> "Extract All..." ->
     "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 1 changed file -> "Commit to main" -> "Push origin"
  3. ~1 min, then Ctrl+Shift+R.

Replaced file:
  AP_REC\frontend\src\api.js
