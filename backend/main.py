"""
AP Reconciliation — FastAPI Backend
"""
import os, shutil, tempfile, uuid, json
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from reconciliation_engine import run_reconciliation
from rename_engine import propose_renames, build_zip

app = FastAPI(title="AP Reconciliation API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

APP_PASSWORD = os.getenv("APP_PASSWORD", "reconcile2026")
bearer = HTTPBearer()

def require_auth(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    if creds.credentials != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

UPLOAD_DIR = Path(tempfile.mkdtemp())

# ── Health ─────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}

# ── Auth ───────────────────────────────────────────────────────────────────
@app.post("/auth")
def auth(body: dict):
    if body.get("password") != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="Wrong password")
    return {"token": APP_PASSWORD}

# ── Reconciliation ─────────────────────────────────────────────────────────
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
        gl_path = job_dir / gl_file.filename
        gl_path.write_bytes(await gl_file.read())
        stmt_paths = []
        for s in statements:
            p = job_dir / s.filename
            p.write_bytes(await s.read())
            stmt_paths.append(str(p))
        logs = []
        result_bytes, output_filename, reconciled, skipped = run_reconciliation(
            str(gl_path), stmt_paths, log_fn=logs.append,
        )
        out_path = job_dir / "AP_REC_result.xlsx"
        out_path.write_bytes(result_bytes)
        return JSONResponse({
            "job_id":       job_id,
            "logs":         logs,
            "skipped":      list(skipped),
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

# ── File Namer — propose renames ───────────────────────────────────────────
@app.post("/rename/propose")
async def rename_propose(
    files: list[UploadFile] = File(...),
    _: bool = Depends(require_auth),
):
    job_id  = str(uuid.uuid4())
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir()
    try:
        paths = []
        for f in files:
            p = job_dir / f.filename
            p.write_bytes(await f.read())
            paths.append(str(p))
        logs = []
        proposals = propose_renames(paths, log_fn=logs.append)
        return JSONResponse({
            "job_id":    job_id,
            "proposals": proposals,
            "logs":      logs,
        })
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))

# ── File Namer — download zip with confirmed names ─────────────────────────
@app.post("/rename/download/{job_id}")
async def rename_download(
    job_id: str,
    body: dict,
    _: bool = Depends(require_auth),
):
    job_dir = UPLOAD_DIR / job_id
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    rename_map = body.get("rename_map", {})  # { original: new_name }
    paths = [str(p) for p in job_dir.iterdir() if p.is_file()]
    zip_bytes = build_zip(paths, rename_map)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=renamed_files.zip"},
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
