TRENDS PAGE — INSTALL (no file editing needed)
==============================================

1. Extract this zip directly into your AP_REC repo folder:
   C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC

2. When Windows asks about merging folders → YES
   When it asks about replacing files → REPLACE ALL
   (main.py, api.js, App.jsx, Sidebar.jsx get replaced;
    trends_engine.py and TrendsPage.jsx are new)

3. Open GitHub Desktop → review changes → commit → push.

4. If the Trends page says "Not Found" after Railway deploys:
   Railway → AP_REC service → Deployments → ⋯ on latest → Redeploy
   (clears Docker cache)

5. Delete this README file — it doesn't need to be committed.
