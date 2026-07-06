WAVE 1: USER ACCOUNTS + SAVED GL + LIGHT THEME
==============================================

WHAT THIS ADDS
  1. Individual email+password logins. You are the admin; a "Users" button
     in the header lets you create/remove the 2-5 accounts.
  2. Your GL is SAVED per user. Upload once; leave; come back tomorrow and
     the Trends page loads and analyzes it automatically. Uploading a new
     file replaces the saved one.
  3. A "Light" button in the header toggles a warm off-white theme.
     Choice is remembered per browser.

STEP 1 — DELETE this file from your repo (File Explorer):
  AP_REC\backend\trends_api.py        (unused leftover)

STEP 2 — Extract this zip into:
  C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
  Merge folders: YES.  Replace files: REPLACE ALL.

  New file:
    AP_REC\backend\db.py
  Replaced files:
    AP_REC\backend\main.py
    AP_REC\backend\requirements.txt
    AP_REC\frontend\src\api.js
    AP_REC\frontend\src\App.jsx
    AP_REC\frontend\src\index.css
    AP_REC\frontend\src\pages\LoginPage.jsx
    AP_REC\frontend\src\pages\TrendsPage.jsx

STEP 3 — RAILWAY: add the database (one time, ~1 minute)
  1. railway.app -> open your AP_REC project
  2. Click "+ New" (top right) -> "Database" -> "Add PostgreSQL"
  3. Click your BACKEND service -> "Variables" tab -> "+ New Variable"
     -> click "Add Reference" -> pick Postgres -> DATABASE_URL -> Add
  4. (Recommended) Add two more variables on the backend service:
       ADMIN_EMAIL    = ssahin@casperscompany.com
       ADMIN_PASSWORD = (a password you choose for yourself)
     If you skip this, your first login is:
       email    ssahin@casperscompany.com
       password (your current APP_PASSWORD value)

STEP 4 — GitHub Desktop: commit -> push. Railway + Netlify auto-deploy.
  If anything 404s after deploy: Railway -> Deployments -> Redeploy latest.

STEP 5 — FIRST LOGIN
  Sign in with the admin email/password from Step 3. Click "Users" in the
  header to add your colleagues. Everyone signs in with their own email.

NOTE: until Step 3 is done, the app uses a temporary on-server database
that resets on each deploy. Accounts and saved GLs become permanent the
moment the Postgres variable is added.
