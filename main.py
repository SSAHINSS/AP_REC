"""
AP Reconciliation — FastAPI Backend
"""
import os, shutil, tempfile, uuid
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from reconciliation_engine import run_reconciliation

# ── App ───────────────────────────────────────────────────────────────────
app = FastAPI(title="AP Reconciliation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # lock this down to your domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Auth (simple password check — swap for JWT/OAuth when selling) ─────────
APP_PASSWORD = os.getenv("APP_PASSWORD", "reconcile2026")
bearer = HTTPBearer()

def require_auth(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    if creds.credentials != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

# ── Temp file storage (use S3/GCS in production) ──────────────────────────
UPLOAD_DIR = Path(tempfile.mkdtemp())

# ── Routes ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth")
def auth(body: dict):
    """Exchange password for a token (token IS the password for now)."""
    if body.get("password") != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="Wrong password")
    return {"token": APP_PASSWORD}

@app.post("/reconcile")
async def reconcile(
    gl_file: UploadFile = File(...),
    statements: list[UploadFile] = File(...),
    _: bool = Depends(require_auth),
):
    job_id = str(uuid.uuid4())
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir()

    try:
        # Save GL
        gl_path = job_dir / gl_file.filename
        gl_path.write_bytes(await gl_file.read())

        # Save statements
        stmt_paths = []
        for s in statements:
            p = job_dir / s.filename
            p.write_bytes(await s.read())
            stmt_paths.append(str(p))

        # Run engine
        logs = []
        result_bytes = run_reconciliation(
            str(gl_path),
            stmt_paths,
            log_fn=logs.append,
        )

        # Save output
        out_path = job_dir / "AP_REC_result.xlsx"
        out_path.write_bytes(result_bytes)

        return JSONResponse({
            "job_id": job_id,
            "logs": logs,
            "download_url": f"/download/{job_id}",
        })

    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{job_id}")
def download(job_id: str, _: bool = Depends(require_auth)):
    out_path = UPLOAD_DIR / job_id / "AP_REC_result.xlsx"
    if not out_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(out_path),
        filename="AP_REC_result.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
