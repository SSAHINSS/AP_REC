FIX: CARDHOLDER DRILL-DOWN NOW SHOWS THE VENDOR
================================================
Drilling into a cardholder's spend now shows WHO WAS PAID: the redundant
CARDHOLDER column (the person is already in the window title) is replaced
by a sortable VENDOR column. Vendor drill-downs are unchanged (they keep
the cardholder column, since the vendor is already the window title).

DEPLOY (Netlify-only, 1 file):
  1. Downloads -> right-click vendor_in_drilldown.zip -> "Extract All..."
     -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 1 changed file -> "Commit to main" -> "Push origin"
  3. ~1 min, then Ctrl+Shift+R.

Replaced file:
  AP_REC\frontend\src\components\DetailWindow.jsx
