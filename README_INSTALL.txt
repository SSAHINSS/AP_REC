FIX: ACCRUAL BUILDER SELECTORS DEAD / NO VENDOR TABLE
======================================================
Cause: the page called the trends API with its arguments in the wrong
order (the function's first argument is an optional GL file), so every
request was malformed and rejected - selectors rendered but nothing
loaded. It also skipped the initial org-wide load that Expense Trends
uses to populate the entity pills and month list.

Now it mirrors Expense Trends' data flow exactly:
  - On open: entities + months load automatically
  - Click an entity: its vendor table loads, grouped by GL group, with
    clickable month numbers (reconciled drill-downs), TYPE chips, and
    the accrue checkbox/amount/account/location controls
  - A visible error card appears if anything fails (including a clear
    message if the backend needs a Railway redeploy)

DEPLOY (Netlify-only, 1 file):
  1. Downloads -> right-click accrual_data_fix.zip -> "Extract All..."
     -> "Browse..." to
     C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
     -> "Select Folder" -> "Extract" -> "Yes" -> "Replace the files"
  2. GitHub Desktop -> 1 changed file -> "Commit to main" -> "Push origin"
  3. ~1 min, then Ctrl+Shift+R.

NOTE: if after this the accrual ACCOUNT dropdown is still empty or an
error card mentions the backend, the backend from the accrual_builder
batch isn't live yet: railway.app -> AP_REC -> "web" -> "Deployments"
-> "..." -> "Redeploy", wait for green, reload the site.

Replaced file:
  AP_REC\frontend\src\pages\AccrualPage.jsx
