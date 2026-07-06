FIX: BLANK TRENDS PAGE
======================
The Trends page was silently skipping its initial analysis due to a
timing bug in the page-load logic (it checked a value that had not
updated yet and bailed out). It now analyzes the saved GL immediately
on open, and shows a clear "upload on Home" card when nothing is saved.

Extract this zip into:
  C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
Merge folders: YES.  Replace file: REPLACE.

Replaced file:
  AP_REC\frontend\src\pages\TrendsPage.jsx

GitHub Desktop: commit -> push. Netlify-only (no Railway change).
