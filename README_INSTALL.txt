FIX: USER MANAGER NO LONGER VANISHES
====================================
The panel used to close on ANY click outside the card - including
releasing a text-selection drag outside it, or a click a few pixels off
a checkbox. Now it closes ONLY via the Close button or the Escape key.
(Also cleaned up React row-key warnings in the user table.)

DEPLOY (Netlify-only, 1 file):
  1. File Explorer -> Downloads -> right-click modal_fix.zip ->
     "Extract All..." -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 1 changed file -> summary -> "Commit to main"
     -> "Push origin".  Then Ctrl+Shift+R after ~1 min.

Replaced file:
  AP_REC\frontend\src\App.jsx
