USER MANAGEMENT + PERMISSIONS + UI CLEANUP  (includes the security fix)
=======================================================================

THIS ZIP CONTAINS EVERYTHING - the admin-password security fix from the
previous batch is included, so upload just this one.

WHAT'S NEW
  1. USER MANAGEMENT PANEL (Users button, admin only):
     - Full list of active users with email + created date
     - Per-module permission checkboxes for each user:
       AP Rec / File Namer / Expense Trends / Payroll (toggle instantly)
     - "reset pw" per user - type a new password inline, click Set
     - Remove user (with confirmation)
     - Add user with chosen module permissions from the start
     - Admins always have all modules + user management
  2. PERMISSIONS ENFORCED EVERYWHERE:
     - Backend: every module endpoint checks the user's permissions
       (403 if not allowed) - not just hidden buttons
     - Frontend: sidebar icons and Home tiles only show allowed modules
     - Existing users are grandfathered with ALL modules until you
       restrict them (safe database migration included - no data loss)
  3. UI CLEANUP:
     - Removed the "Authenticated" badge from the top right
     - Removed the muted description lines next to all page titles
     - Removed "By GL Account" view from Expense Trends (vendor-only now)
  4. SECURITY FIX (from previous batch, included here):
     - Admin password now syncs from the Railway variable on every boot

DEPLOY:
  1. File Explorer -> Downloads -> right-click user_mgmt_and_cleanup.zip
     -> "Extract All..." -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 7 changed files -> summary -> "Commit to main"
     -> "Push origin".
  3. AFTER the push, do the password rotation in Railway:
     railway.app -> AP_REC -> "web" box -> "Variables":
       a. Edit APP_PASSWORD -> new private password only you know
       b. "+ New Variable" -> APP_SECRET -> long random string (30+ chars)
     Railway auto-redeploys. Everyone signs in again once (expected).
  4. Sign in with your NEW password -> click "Users" -> set each
     person's module permissions.

Files:
  replaced AP_REC\backend\main.py
  replaced AP_REC\backend\db.py
  replaced AP_REC\frontend\src\api.js
  replaced AP_REC\frontend\src\App.jsx
  replaced AP_REC\frontend\src\components\Sidebar.jsx
  replaced AP_REC\frontend\src\pages\HomePage.jsx
  replaced AP_REC\frontend\src\pages\TrendsPage.jsx
