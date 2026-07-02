TRENDS PAGE — INSTALL STEPS
============================

1. EXTRACT THIS ZIP directly into your AP_REC repo folder
   (C:\Users\SannySahin\OneDrive - Caspers Company\Documents\GitHub\AP_REC)
   When Windows asks about merging folders, say YES.
   When it asks about replacing App.jsx and Sidebar.jsx, say REPLACE.

   The files land like this:
     backend\trends_engine.py            (new)
     backend\trends_api.py               (new)
     frontend\src\pages\TrendsPage.jsx   (new)
     frontend\src\components\Sidebar.jsx (replaces existing)
     frontend\src\App.jsx                (replaces existing)

2. EDIT backend\main.py — add these 2 lines right after the "app = FastAPI(" line
   (or after the CORS middleware block if there is one):

     from trends_api import router as trends_router
     app.include_router(trends_router)

3. EDIT frontend\src\api.js — paste this at the VERY BOTTOM of the file:

     export async function analyzeTrends(glFile, entity = '', view = 'vendor') {
       const form = new FormData()
       form.append('gl_file', glFile)
       form.append('entity', entity)
       form.append('view', view)

       const res = await fetch(`${BASE}/trends/analyze`, {
         method: 'POST',
         headers: { Authorization: `Bearer ${getToken()}` },
         body: form,
       })

       if (!res.ok) {
         const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
         throw new Error(err.detail || 'Trends analysis failed')
       }
       return res.json()
     }

4. In GitHub Desktop: review the changes, commit, push.

5. If /trends/analyze returns 404 after Railway deploys:
   Railway -> AP_REC service -> Deployments -> three-dot menu on latest -> Redeploy
   (clears the Docker cache — the usual gotcha)

DELETE this README before or after committing, it does not need to be in the repo.
