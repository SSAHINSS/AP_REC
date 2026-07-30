RECONCILIATION ENGINE FIX: OCR + BUSH BROTHERS + SOURCE BOOKS + MORE
=====================================================================
Fixes the statement-extraction errors your users reported:

1. SCANNED/IMAGE STATEMENTS (Auto-Chlor and similar) now OCR properly.
   The engine used to only OCR when text extraction returned NOTHING;
   scanned pages that returned a tiny garbled sliver (e.g. 111 characters)
   slipped through and failed. Now it detects insufficient/garbled text and
   runs OCR, using PyMuPDF rendering (no poppler dependency) then Tesseract.
   Auto-Chlor went from 111 unreadable chars -> full statement, total $491.28.

2. BUSH BROTHERS - the "Total Due" box total is now read ($13,836.67), and
   the invoice ledger (Date/Type/Reference/Original/Applied/Balance) is now
   parsed: 2 rows -> 18 rows.

3. SOURCE BOOKS - "Total $ 1,008.50" now reads, and the IN/CN document rows
   now parse (0 -> 4 rows, summing exactly to the statement total).

4. General: added "Total Due" and "Total $" (no-colon) total patterns, which
   will help other vendors with the same layouts.

Nothing else in the engine changed - all existing vendor formats still work
(verified end-to-end: a full LIB reconciliation runs with 0 skipped files).

DEPLOY (backend-only):
  1. File Explorer -> Downloads -> right-click recon_extraction_fix.zip ->
     "Extract All..." -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 1 changed file -> summary -> "Commit to main"
     -> "Push origin".
  3. Wait ~2 min for Railway. If extraction still fails after deploy,
     railway.app -> AP_REC -> "web" box -> "Deployments" -> "..." on
     newest -> "Redeploy".

  NOTE: OCR relies on Tesseract + the PDF renderer, which are already
  installed on Railway (in your Dockerfile). No infra change needed.

Replaced file:
  AP_REC\backend\reconciliation_engine.py
