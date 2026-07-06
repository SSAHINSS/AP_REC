AP TRENDS: FULL 14-MONTH WINDOW + SPILLOVER MONTH + ANALYSIS-MONTH EMPHASIS
===========================================================================

WHAT CHANGED
  With June 2026 selected, the table now shows June 2025 through JULY 2026:
  - 12 months BEFORE the analysis month (columns exist even where the GL
    has no data yet - they show as empty instead of being dropped)
  - the ANALYSIS month itself - bold + orange header. All flags key off
    this month.
  - ONE month AFTER it (spillover check) - so a bill accidentally posted
    into the next period is visible right next to the month it belonged in.
    The spillover column never enters the flag statistics.
  Default month logic unchanged (prior month through the 10th).

STEP 1 - Extract this zip into:
  C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC
  Merge folders: YES.  Replace files: REPLACE ALL.

  Replaced files:
    AP_REC\backend\trends_engine.py
    AP_REC\frontend\src\pages\TrendsPage.jsx

STEP 2 - GitHub Desktop: type a summary, "Commit to main", then "Push origin".
  Railway + Netlify auto-deploy (backend changed - if the window looks
  unchanged after deploy, Railway -> Deployments -> Redeploy latest).
