HOME PAGE REDESIGN + TIMESTAMP FIX
==================================
1. "IMPOSSIBLE" TIMESTAMP EXPLAINED & FIXED: the server stores times in
   UTC, but the timezone marker was being dropped, so your browser showed
   the UTC clock as if it were local - 4 hours in the future for Tampa.
   "1:21:44 PM" was really 9:21:44 AM your time. Timestamps now carry
   their timezone so the browser converts correctly.
2. WHY IT SAID A FILE WAS UPLOADED TODAY: attaching a GL inside AP Rec /
   Expense Trends / Payroll ALSO updates the saved copy - it is not only
   the Home dropzone. Someone on your login ran a module with a GL
   attached at 9:21 AM. The label now honestly reads "last updated" and
   the upload panel notes this behavior. (Recommend: separate accounts
   for your users via the Users button.)
3. HOME PAGE REORDERED: module tiles are now the first thing you see.
   The GL area is a compact status bar underneath, with the dropzone
   hidden behind a "Replace GL" button (it auto-opens only when no GL is
   on file). Also renamed the stale "Trends" tile to "Expense Trends".

DEPLOY:
  1. File Explorer -> Downloads -> right-click home_and_timestamp_fix.zip
     -> "Extract All..." -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 2 changed files -> summary -> "Commit to main"
     -> "Push origin".
  3. Backend changed: wait ~2 min; if timestamps still look 4h ahead,
     railway.app -> AP_REC -> "web" box -> "Deployments" -> "..." ->
     "Redeploy". Then Ctrl+Shift+R the site.

Replaced files:
  AP_REC\backend\main.py
  AP_REC\frontend\src\pages\HomePage.jsx
