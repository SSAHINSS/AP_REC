POPUP FIXES: OPENS WHERE YOU ARE + FROZEN HEADERS + RENAME
==========================================================
1. The drill-down window now opens centered in your CURRENT view -
   no more scrolling up to find it after clicking a number at the
   bottom of a long table.
2. The column headers inside the popup are now frozen - scroll down
   through transactions and the DATE/ACCOUNT/AMOUNT/etc. headers stay
   visible at the top of the window.
3. Renamed the top toggle "Credit Cards by Cardholder" -> "Credit Card
   Expenses" (and the section heading to match).

DEPLOY (Netlify-only, no backend change):
  1. File Explorer -> Downloads -> right-click popup_fixes.zip ->
     "Extract All..." -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 3 changed files -> summary -> "Commit to main"
     -> "Push origin".

Replaced files:
  AP_REC\frontend\src\components\DetailWindow.jsx
  AP_REC\frontend\src\pages\TrendsPage.jsx
  AP_REC\frontend\src\pages\CardholderView.jsx
