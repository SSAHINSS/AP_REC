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
from trends_engine import (analyze as analyze_trends, detail as trends_detail_fn,
                            cc_by_cardholder as cc_holder_fn, cardholder_detail as cardholder_detail_fn)
from trends_report import build_report
from payroll_engine import (accrual as payroll_accrual, trends as payroll_trends,
                            rate_detail as payroll_rate_detail, cell_detail as payroll_cell_detail)
from db import (init_db, get_session, User, store_gl, load_gl, delete_gl,
                gl_overview, get_accrual_draft, put_accrual_draft,
                latest_credit_account, SessionLocal, USING_SQLITE)


def _iso_utc(dt):
    """Timestamps come back from the DB naive (tz dropped). Re-attach UTC so
    browsers convert to the user's local time instead of showing UTC as local."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

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


MODULES = ("aprec", "filenamer", "trends", "payroll", "accruals")


def _perms(user: User):
    """Admins get everything; others get their stored list (default: all)."""
    if user.is_admin:
        return list(MODULES)
    raw = getattr(user, "permissions", None)
    if raw is None or raw == "":
        return list(MODULES)
    return [p for p in raw.split(",") if p in MODULES]


def require_module(mod: str):
    def _dep(user: User = Depends(require_auth)) -> User:
        if mod not in _perms(user):
            raise HTTPException(status_code=403,
                                detail=f"Your account doesn't have access to this module")
        return user
    return _dep


def require_admin(user: User = Depends(require_auth)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user


@app.on_event("startup")
def _startup():
    init_db()
    # Bootstrap/sync the admin account. The password hash is kept in sync with
    # the ADMIN_PASSWORD (or APP_PASSWORD) variable on EVERY boot, so rotating
    # the variable in Railway rotates the admin login — critical because the
    # legacy value was the old shared team password.
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == ADMIN_EMAIL.lower().strip()).first()
        if admin is None:
            db.add(User(email=ADMIN_EMAIL.lower().strip(),
                        password_hash=_hash_pw(ADMIN_PASSWORD),
                        is_admin=True))
            db.commit()
        else:
            changed = False
            if not _verify_pw(ADMIN_PASSWORD, admin.password_hash):
                admin.password_hash = _hash_pw(ADMIN_PASSWORD)
                changed = True
            if not admin.is_admin:
                admin.is_admin = True
                changed = True
            if changed:
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
    return {"token": _make_token(user), "email": user.email, "is_admin": user.is_admin,
            "permissions": _perms(user)}


@app.get("/me")
def me(user: User = Depends(require_auth)):
    return {"email": user.email, "is_admin": user.is_admin, "permissions": _perms(user)}

# ── User management (admin only) ────────────────────────────────────────────
@app.get("/users")
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_session)):
    return [{"id": u.id, "email": u.email, "is_admin": u.is_admin,
             "permissions": _perms(u), "created_at": _iso_utc(u.created_at)}
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
    perms = body.get("permissions")
    if isinstance(perms, list):
        perms_str = ",".join(p for p in perms if p in MODULES)
    else:
        perms_str = ",".join(MODULES)
    u = User(email=email, password_hash=_hash_pw(password),
             is_admin=bool(body.get("is_admin", False)),
             permissions=perms_str)
    db.add(u); db.commit()
    return {"id": u.id, "email": u.email, "is_admin": u.is_admin, "permissions": _perms(u)}


@app.patch("/users/{user_id}")
def update_user(user_id: int, body: dict, admin: User = Depends(require_admin),
                db: Session = Depends(get_session)):
    """Admin management: reset password, set module permissions, toggle admin."""
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    if "password" in body and body["password"]:
        if len(body["password"]) < 6:
            raise HTTPException(status_code=422, detail="Password must be at least 6 characters")
        u.password_hash = _hash_pw(body["password"])

    if "permissions" in body and isinstance(body["permissions"], list):
        u.permissions = ",".join(p for p in body["permissions"] if p in MODULES)

    if "is_admin" in body:
        if user_id == admin.id and not body["is_admin"]:
            raise HTTPException(status_code=422, detail="You can't remove your own admin access")
        u.is_admin = bool(body["is_admin"])

    db.commit()
    return {"id": u.id, "email": u.email, "is_admin": u.is_admin, "permissions": _perms(u)}


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
    statements: list[UploadFile] = File(...),
    gl_file: UploadFile | None = File(None),
    user: User = Depends(require_module("aprec")),
    db: Session = Depends(get_session),
):
    job_id = str(uuid.uuid4())
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir()
    try:
        if gl_file is not None and gl_file.filename:
            gl_bytes = await gl_file.read()
            gl_name = gl_file.filename
            # remember it as this user's AP-Rec-specific GL for next time
            store_gl(db, user.id, gl_name, gl_bytes, scope="aprec")
        else:
            stored = load_gl(db, user.id, scope="aprec")
            if not stored:
                raise HTTPException(status_code=422,
                                    detail="No GL on file — attach one or upload a GL first")
            gl_name, gl_bytes, _up, _sc = stored
        gl_path = job_dir / gl_name
        gl_path.write_bytes(gl_bytes)
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
def download(job_id: str, user: User = Depends(require_module("aprec"))):
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
    user: User = Depends(require_module("filenamer")),
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
    user: User = Depends(require_module("filenamer")),
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
@app.post("/gl/upload")
async def gl_upload(
    gl_file: UploadFile = File(...),
    scope: str = Form("shared"),
    user: User = Depends(require_auth),
    db: Session = Depends(get_session),
):
    if scope not in ("shared", "aprec", "trends", "payroll"):
        raise HTTPException(status_code=422, detail="Bad scope")
    csv_bytes = await gl_file.read()
    store_gl(db, user.id, gl_file.filename, csv_bytes, scope=scope)
    # quick summary for the Home page
    try:
        import io as _io
        import pandas as _pd
        _df = _pd.read_csv(_io.BytesIO(csv_bytes), usecols=["Posting date", "Location ID"],
                           low_memory=False)
        _d = _pd.to_datetime(_df["Posting date"], errors="coerce").dropna()
        _ents = (_df["Location ID"].fillna("").astype(str)
                 .str.split("-").str[0].str.upper())
        summary = {
            "rows": int(len(_df)),
            "first_month": _d.min().strftime("%Y-%m") if len(_d) else None,
            "last_month": _d.max().strftime("%Y-%m") if len(_d) else None,
            "entities": int(_ents[_ents != ""].nunique()),
        }
    except Exception:
        summary = {"rows": None, "first_month": None, "last_month": None, "entities": None}
    return {"stored": True, "filename": gl_file.filename,
            "uploaded_at": datetime.now(timezone.utc).isoformat(), **summary}


@app.get("/gl/status")
def gl_status(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    """Per-user GL slots: the shared GL plus any module-specific overrides."""
    ov = gl_overview(db, user.id)
    def fmt(s):
        r = ov.get(s)
        return {"filename": r["filename"], "uploaded_at": _iso_utc(r["uploaded_at"])} if r else None
    return {"has_gl": "shared" in ov,
            "shared": fmt("shared"),
            "overrides": {s: fmt(s) for s in ("aprec", "trends", "payroll")},
            # legacy fields so nothing breaks mid-deploy
            "filename": (ov.get("shared") or {}).get("filename"),
            "uploaded_at": _iso_utc((ov.get("shared") or {}).get("uploaded_at"))}


@app.delete("/gl/override/{scope}")
def gl_override_delete(scope: str, user: User = Depends(require_auth),
                       db: Session = Depends(get_session)):
    if scope not in ("aprec", "trends", "payroll"):
        raise HTTPException(status_code=422, detail="Bad scope")
    n = delete_gl(db, user.id, scope)
    return {"removed": n, "scope": scope}


@app.post("/trends/analyze")
async def trends_analyze(
    gl_file: UploadFile | None = File(None),
    entity: str = Form(""),
    view: str = Form("vendor"),
    period: str = Form(""),
    user: User = Depends(require_module("trends")),
    db: Session = Depends(get_session),
):
    if view not in ("vendor", "account"):
        raise HTTPException(status_code=422, detail="view must be 'vendor' or 'account'")

    if gl_file is not None and gl_file.filename:
        csv_bytes = await gl_file.read()
        store_gl(db, user.id, gl_file.filename, csv_bytes, scope="trends")
        filename = gl_file.filename
        uploaded_at = datetime.now(timezone.utc)
    else:
        stored = load_gl(db, user.id, scope="trends")
        if not stored:
            raise HTTPException(status_code=422,
                                detail="No GL on file — upload one to begin")
        filename, csv_bytes, uploaded_at, _sc = stored

    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(csv_bytes)
            tmp = f.name
        result = analyze_trends(tmp, entity=entity or None, view=view, period=period or None)
        result["gl_filename"] = filename
        result["gl_uploaded_at"] = _iso_utc(uploaded_at)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


# ── Payroll — accrual calculator + payroll trends ───────────────────────────
@app.post("/payroll/accrual")
async def payroll_accrual_ep(
    gl_file: UploadFile | None = File(None),
    month_end: str = Form(...),
    entity: str = Form(""),
    overrides: str = Form("{}"),
    user: User = Depends(require_module("payroll")),
    db: Session = Depends(get_session),
):
    if gl_file is not None and gl_file.filename:
        csv_bytes = await gl_file.read()
        store_gl(db, user.id, gl_file.filename, csv_bytes, scope="payroll")
    else:
        stored = load_gl(db, user.id, scope="payroll")
        if not stored:
            raise HTTPException(status_code=422, detail="No GL on file — upload one first")
        _fn, csv_bytes, _up, _sc = stored
    try:
        ov = json.loads(overrides or "{}")
    except Exception:
        ov = {}
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(csv_bytes); tmp = f.name
        return payroll_accrual(tmp, month_end, entity=entity or None, schedule_overrides=ov)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


@app.post("/payroll/trends")
async def payroll_trends_ep(
    entity: str = Form(""),
    period: str = Form(""),
    user: User = Depends(require_module("payroll")),
    db: Session = Depends(get_session),
):
    stored = load_gl(db, user.id, scope="payroll")
    if not stored:
        raise HTTPException(status_code=422, detail="No GL on file — upload one first")
    _fn, csv_bytes, _up, _sc = stored
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(csv_bytes); tmp = f.name
        return payroll_trends(tmp, entity=entity or None, period=period or None)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


@app.post("/payroll/detail")
async def payroll_detail_ep(
    kind: str = Form(...),           # "rate" | "cell"
    entity: str = Form(""),
    category: str = Form(...),
    month_end: str = Form(""),        # rate mode
    schedule: str = Form("cohort1"),  # rate mode
    month: str = Form(""),            # cell mode ("YYYY-MM")
    user: User = Depends(require_module("payroll")),
    db: Session = Depends(get_session),
):
    stored = load_gl(db, user.id, scope="payroll")
    if not stored:
        raise HTTPException(status_code=422, detail="No GL on file — upload one first")
    _fn, csv_bytes, _up, _sc = stored
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(csv_bytes); tmp = f.name
        if kind == "rate":
            if not (entity and month_end):
                raise HTTPException(status_code=422, detail="rate detail needs entity + month_end")
            return payroll_rate_detail(tmp, entity, month_end, category, schedule)
        elif kind == "cell":
            if not month:
                raise HTTPException(status_code=422, detail="cell detail needs month")
            return payroll_cell_detail(tmp, category, month, entity=entity or None)
        raise HTTPException(status_code=422, detail="kind must be 'rate' or 'cell'")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)



@app.post("/trends/detail")
async def trends_detail_ep(
    label: str = Form(...),
    view: str = Form("vendor"),
    entity: str = Form(""),
    month: str = Form(""),
    period: str = Form(""),
    comparisons: str = Form(""),
    group: str = Form(""),
    include_sales: bool = Form(False),
    user: User = Depends(require_module("trends")),
    db: Session = Depends(get_session),
):
    stored = load_gl(db, user.id, scope="trends")
    if not stored:
        raise HTTPException(status_code=422, detail="No GL on file — upload one first")
    _fn, csv_bytes, _up, _sc = stored
    cmps = [c for c in comparisons.split(",") if c] if comparisons else None
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(csv_bytes); tmp = f.name
        return trends_detail_fn(tmp, label, view=view, entity=entity or None,
                                month=month or None, period=period or None,
                                comparisons=cmps, group=group or None,
                                include_sales=include_sales)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


@app.post("/trends/export")
async def trends_export_ep(
    entity: str = Form(""),
    view: str = Form("vendor"),
    period: str = Form(""),
    user: User = Depends(require_module("trends")),
    db: Session = Depends(get_session),
):
    stored = load_gl(db, user.id, scope="trends")
    if not stored:
        raise HTTPException(status_code=422, detail="No GL on file — upload one first")
    _fn, csv_bytes, _up, _sc = stored
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(csv_bytes); tmp = f.name
        xlsx, fname = build_report(tmp, entity=entity or None, view=view, period=period or None)
        return Response(
            content=xlsx,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={fname}"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)



@app.post("/trends/cardholders")
async def trends_cardholders_ep(
    entities: str = Form(""),      # comma-separated entity prefixes
    holders: str = Form(""),       # comma-separated cardholder names
    start: str = Form(""),
    end: str = Form(""),
    user: User = Depends(require_module("trends")),
    db: Session = Depends(get_session),
):
    stored = load_gl(db, user.id, scope="trends")
    if not stored:
        raise HTTPException(status_code=422, detail="No GL on file — upload one first")
    _fn, csv_bytes, _up, _sc = stored
    ents = [e for e in entities.split(",") if e] or None
    hlds = [h for h in holders.split("|") if h] or None   # names may contain commas → pipe-delimit
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(csv_bytes); tmp = f.name
        return cc_holder_fn(tmp, entities=ents, holders=hlds, start=start or None, end=end or None)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


@app.post("/trends/cardholder_detail")
async def trends_cardholder_detail_ep(
    holder: str = Form(...),
    entities: str = Form(""),
    start: str = Form(""),
    end: str = Form(""),
    user: User = Depends(require_module("trends")),
    db: Session = Depends(get_session),
):
    stored = load_gl(db, user.id, scope="trends")
    if not stored:
        raise HTTPException(status_code=422, detail="No GL on file — upload one first")
    _fn, csv_bytes, _up, _sc = stored
    ents = [e for e in entities.split(",") if e] or None
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(csv_bytes); tmp = f.name
        return cardholder_detail_fn(tmp, holder, entities=ents, start=start or None, end=end or None)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)



# ── Accrual Builder (experimental) ─────────────────────────────────────────
from accrual_engine import (account_choices, row_defaults as accrual_row_defaults,
                            build_je_csv)


def _with_gl(db, user, fn):
    stored = load_gl(db, user.id, scope="trends")   # same GL as Expense Trends
    if not stored:
        raise HTTPException(status_code=422, detail="No GL on file — upload one to begin")
    _fn, csv_bytes, _up, _sc = stored
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(csv_bytes); tmp = f.name
        return fn(tmp)
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


@app.get("/accrual/draft")
def accrual_draft_get(entity: str, period: str,
                      user: User = Depends(require_module("accruals")),
                      db: Session = Depends(get_session)):
    raw = get_accrual_draft(db, user.id, entity.upper(), period)
    draft = json.loads(raw) if raw else {"rows": {}, "credit_acct": None}
    if not draft.get("credit_acct"):
        draft["credit_acct"] = latest_credit_account(db, user.id)
    return draft


@app.put("/accrual/draft")
def accrual_draft_put(body: dict,
                      user: User = Depends(require_module("accruals")),
                      db: Session = Depends(get_session)):
    entity = (body.get("entity") or "").upper()
    period = body.get("period") or ""
    if not entity or not period:
        raise HTTPException(status_code=422, detail="entity and period required")
    put_accrual_draft(db, user.id, entity, period,
                      json.dumps({"rows": body.get("rows") or {},
                                  "credit_acct": body.get("credit_acct")}))
    return {"ok": True}


@app.get("/accrual/accounts")
def accrual_accounts(user: User = Depends(require_module("accruals")),
                     db: Session = Depends(get_session)):
    return _with_gl(db, user, lambda tmp: account_choices(tmp))


@app.post("/accrual/rowinfo")
def accrual_rowinfo(body: dict,
                    user: User = Depends(require_module("accruals")),
                    db: Session = Depends(get_session)):
    return _with_gl(db, user, lambda tmp: accrual_row_defaults(
        tmp, body.get("entity") or "", body.get("group") or "",
        body.get("label") or "", body.get("period") or ""))


@app.post("/accrual/export")
def accrual_export(body: dict,
                   user: User = Depends(require_module("accruals")),
                   db: Session = Depends(get_session)):
    def run(tmp):
        try:
            csv_bytes, fname, summary = build_je_csv(
                tmp, body.get("entity") or "", body.get("period") or "",
                body.get("credit_acct") or "", body.get("lines") or [],
                credit_location=body.get("credit_location"))
        except ValueError as ve:
            raise HTTPException(status_code=422,
                                detail={"validation_errors": ve.args[0]})
        return Response(content=csv_bytes, media_type="text/csv",
                        headers={"Content-Disposition": f"attachment; filename={fname}",
                                 "X-JE-Summary": json.dumps(summary)})
    return _with_gl(db, user, run)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
