FIX: BLANK PAGE AFTER USER-MGMT DEPLOY
=======================================
Cause: Sidebar.jsx referenced getPerms() but was missing its import (my
build script failed to insert it because that file had no existing import
lines to anchor on). Anyone already signed in loaded straight into the
sidebar, hit the missing function, and the whole app went blank.

Fix: the one missing import line. Verified by rendering the app in all
three states (signed out / admin / limited user) plus a full production
build - all clean.

DEPLOY (Netlify-only, 1 file):
  1. File Explorer -> Downloads -> right-click blank_page_fix.zip ->
     "Extract All..." -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 1 changed file -> summary -> "Commit to main"
     -> "Push origin".
  3. Wait ~1-2 min for Netlify, then Ctrl+Shift+R the site.

Replaced file:
  AP_REC\frontend\src\components\Sidebar.jsx
