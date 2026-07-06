"""
AP Reconciliation — FastAPI Backend
Path: backend/main.py
"""
import os, shutil, tempfile, uuid, json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import bcrypt as _bcrypt
from sqlalchemy.orm import Session

from reconciliation_engine import run_reconciliation
from rename_engine import propose_renames, build_zip
from trends_engine import analyze as analyze_trends
from db import init_db, get_session, User, store_gl, load_gl, SessionLocal, USING_SQLITE

app = FastAPI(title="AP Reconciliation API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Auth config ─────────────────────────────────────────────────────────────
# JWT secret: set APP_SECRET in Railway. Falls back to APP_PASSWORD so nothing
# breaks before you set it.
APP_SECRET = os.getenv("APP_SECRET", os.getenv("APP_PASSWORD", "reconcile2026"))
TOKEN_DAYS = 30
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "ssahin@casperscompany.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", os.getenv("APP_PASSWORD", "reconcile2026"))

bearer = HTTPBearer()


def _hash_pw(p: str) -> str:
    return _bcrypt.hashpw(p.encode()[:72], _bcrypt.gensalt()).decode()


def _verify_pw(p: str, h: str) -> bool:
    try:
        return _bcrypt.checkpw(p.encode()[:72], h.encode())
    except Exception:
        return False


def _make_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "admin": bool(user.is_admin),
        "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_DAYS),
    }
    return jwt.encode(payload, APP_SECRET, algorithm="HS256")


def require_auth(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_session),
) -> User:
    try:
        payload = jwt.decode(creds.credentials, APP_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired — sign in again")
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


def require_admin(user: User = Depends(require_auth)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user


@app.on_event("startup")
def _startup():
    init_db()
    # Bootstrap the first admin if no users exist
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(User(email=ADMIN_EMAIL.lower().strip(),
                        password_hash=_hash_pw(ADMIN_PASSWORD),
                        is_admin=True))
            db.commit()
    finally:
        db.close()


UPLOAD_DIR = Path(tempfile.mkdtemp())

# ── Health ─────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok",
            "db": "sqlite (add Postgres for persistence)" if USING_SQLITE else "postgres"}

# ── Auth ───────────────────────────────────────────────────────────────────
@app.post("/auth")
def auth(body: dict, db: Session = Depends(get_session)):
    email = (body.get("email") or "").lower().strip()
    password = body.get("password") or ""
    user = db.query(User).filter(User.email == email).first()
    if not user or not _verify_pw(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    return {"token": _make_token(user), "email": user.email, "is_admin": user.is_admin}


@app.get("/me")
def me(user: User = Depends(require_auth)):
    return {"email": user.email, "is_admin": user.is_admin}

# ── User management (admin only) ────────────────────────────────────────────
@app.get("/users")
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    return [{"id": u.id, "email": u.email, "is_admin": u.is_admin}
            for u in db.query(User).order_by(User.id).all()]


@app.post("/users")
def create_user(body: dict, admin: User = Depends(require_admin),
                db: Session = Depends(get_session)):
    email = (body.get("email") or "").lower().strip()
    password = body.get("password") or ""
    if not email or "@" not in email:
        raise HTTPException(status_code=422, detail="Valid email required")
    if len(password) < 6:
        raise HTTPException(status_code=422, detail="Password must be at least 6 characters")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="That email already exists")
    u = User(email=email, password_hash=_hash_pw(password),
             is_admin=bool(body.get("is_admin", False)))
    db.add(u); db.commit()
    return {"id": u.id, "email": u.email, "is_admin": u.is_admin}


@app.delete("/users/{user_id}")
def delete_user(user_id: int, admin: User = Depends(require_admin),
                db: Session = Depends(get_session)):
    if user_id == admin.id:
        raise HTTPException(status_code=422, detail="You can't delete your own account")
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(u); db.commit()
    return {"deleted": user_id}

# ── Reconciliation ─────────────────────────────────────────────────────────
@app.post("/reconcile")
async def reconcile(
    gl_file: UploadFile = File(...),
    statements: list[UploadFile] = File(...),
    user: User = Depends(require_auth),
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
def download(job_id: str, user: User = Depends(require_auth)):
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
    user: User = Depends(require_auth),
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
    user: User = Depends(require_auth),
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

# ── Expense Trends — vendor x month analysis with flags ────────────────────
# GL persistence: uploading a file STORES it for the user (replacing any
# previous one). Calling without a file re-uses the stored GL, so you can
# leave and come back tomorrow without re-uploading.
@app.get("/gl/status")
def gl_status(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    stored = load_gl(db, user.id)
    if not stored:
        return {"has_gl": False}
    filename, _bytes, uploaded_at = stored
    return {"has_gl": True, "filename": filename,
            "uploaded_at": uploaded_at.isoformat() if uploaded_at else None}


@app.post("/trends/analyze")
async def trends_analyze(
    gl_file: UploadFile | None = File(None),
    entity: str = Form(""),
    view: str = Form("vendor"),
    period: str = Form(""),
    user: User = Depends(require_auth),
    db: Session = Depends(get_session),
):
    if view not in ("vendor", "account"):
        raise HTTPException(status_code=422, detail="view must be 'vendor' or 'account'")

    if gl_file is not None and gl_file.filename:
        csv_bytes = await gl_file.read()
        store_gl(db, user.id, gl_file.filename, csv_bytes)
        filename = gl_file.filename
        uploaded_at = datetime.now(timezone.utc)
    else:
        stored = load_gl(db, user.id)
        if not stored:
            raise HTTPException(status_code=422,
                                detail="No GL on file — upload one to begin")
        filename, csv_bytes, uploaded_at = stored

    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(csv_bytes)
            tmp = f.name
        result = analyze_trends(tmp, entity=entity or None, view=view, period=period or None)
        result["gl_filename"] = filename
        result["gl_uploaded_at"] = uploaded_at.isoformat() if uploaded_at else None
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
