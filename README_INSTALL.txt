FIX: "permissions is not defined" IN USER MANAGER
==================================================
Cause: the createUser function was missing its new "permissions"
parameter (the automated edit missed the function's actual signature),
so adding a user referenced a variable that didn't exist.
Also hardened the permission checkboxes so they can never crash even if
the backend response is stale.

DEPLOY (Netlify-only, 2 files):
  1. File Explorer -> Downloads -> right-click permissions_error_fix.zip
     -> "Extract All..." -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 2 changed files -> summary -> "Commit to main"
     -> "Push origin".  ~1 min, then Ctrl+Shift+R.

ALSO: if toggling a checkbox or "reset pw" gives "Method Not Allowed" or
"Not Found", the BACKEND from the big batch isn't live yet:
  railway.app -> AP_REC -> "web" box -> "Deployments" -> "..." on the
  newest -> "Redeploy" -> wait for green Success.

Replaced files:
  AP_REC\frontend\src\api.js
  AP_REC\frontend\src\App.jsx
