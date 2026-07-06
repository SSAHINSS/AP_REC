FIX: CONSISTENT LOGO LETTERFORMS + AUTH AUTO-RECOVERY
=====================================================

1. LOGOS — every letter now comes from ONE canonical pixel font:
   - PAYROLL and APRS logos had a clipped R and P (missing the right
     pixel column) — rebuilt full-width, identical to AP-REC's.
   - TRENDS had a home-made N — now uses FILE-NMR's true N.
   - FILE-NMR's E had its crossbar one row higher than AP-REC's E —
     patched so both E's match.

2. UNAUTHORIZED ON UPLOAD — your browser was holding the old
   pre-accounts sign-in token. The app now detects any 401, signs you
   out automatically, and returns you to the login screen.
   ONE-TIME STEP after deploying: click Sign out, then sign back in
   with your email + password. Uploads will work.

Extract this zip into:
  C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
Merge folders: YES.  Replace files: REPLACE ALL.

Replaced files:
  AP_REC\frontend\src\api.js
  AP_REC\frontend\src\App.jsx
  AP_REC\frontend\src\components\TrendsLogo.jsx
  AP_REC\frontend\src\components\PayrollLogo.jsx
  AP_REC\frontend\src\components\HomeLogo.jsx
  AP_REC\frontend\src\components\FileNamerLogo.jsx

GitHub Desktop: commit -> push. Netlify-only (no Railway change).
