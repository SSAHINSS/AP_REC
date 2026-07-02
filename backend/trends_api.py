"""
Trends API router. Wire into main.py with:

    from trends_api import router as trends_router
    app.include_router(trends_router)
"""
import os, tempfile
from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException
from trends_engine import analyze

router = APIRouter(prefix="/trends", tags=["trends"])

APP_PASSWORD = os.environ.get("APP_PASSWORD", "")


def _check_auth(authorization: str):
    token = (authorization or "").replace("Bearer ", "").strip()
    if not APP_PASSWORD or token != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/analyze")
async def trends_analyze(
    gl_file: UploadFile = File(...),
    entity: str = Form(""),
    view: str = Form("vendor"),
    authorization: str = Header(""),
):
    _check_auth(authorization)
    if view not in ("vendor", "account"):
        raise HTTPException(status_code=422, detail="view must be 'vendor' or 'account'")
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(await gl_file.read())
            tmp = f.name
        return analyze(tmp, entity=entity or None, view=view)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)
