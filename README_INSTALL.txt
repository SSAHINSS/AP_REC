FIX: POPUP OPENS IN VIEW (for real this time) + FROZEN MONTH HEADER
====================================================================
1. THE REAL CAUSE of the popup appearing at the top: the page content
   has a CSS transform (the fade-in animation). A transformed parent
   makes "position: fixed" anchor to that parent instead of the screen,
   so the window latched to the top of the page. Fixed by rendering the
   window through a portal directly onto the page body, so it now truly
   floats at your current screen position no matter how far down you are.
2. The main Expense Trends table's month header row is now FROZEN - the
   VENDOR / TYPE / month / TOTAL / FLAG headers stay visible as you
   scroll down the page. (Same applied to the Credit Card Expenses table.)

DEPLOY (Netlify-only, no backend change):
  1. File Explorer -> Downloads -> right-click freeze_and_popup_fix.zip
     -> "Extract All..." -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 3 changed files -> summary -> "Commit to main"
     -> "Push origin".  Then hard-refresh the site (Ctrl+Shift+R).

Replaced files:
  AP_REC\frontend\src\components\DetailWindow.jsx
  AP_REC\frontend\src\pages\TrendsPage.jsx
  AP_REC\frontend\src\pages\CardholderView.jsx
