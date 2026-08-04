"""
Database layer for APRS.
Path: backend/db.py

Uses Railway's DATABASE_URL (Postgres) when present; falls back to a local
SQLite file otherwise so the app boots and works before Postgres is added
(note: SQLite on Railway is ephemeral — add the Postgres service for real
persistence).

Tables:
  users     — individual logins. First admin is bootstrapped from env vars
              ADMIN_EMAIL / ADMIN_PASSWORD (defaults below) on first startup.
  gl_files  — ONE stored GL per user (latest upload replaces the previous).
              CSV bytes are gzip-compressed.
"""
import gzip
import os
from datetime import datetime, timezone

from sqlalchemy import (UniqueConstraint, Boolean, Column, DateTime, ForeignKey, Integer,
                        LargeBinary, String, create_engine)
from sqlalchemy.orm import declarative_base, sessionmaker

# ── Engine ─────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aprs.db")
# Railway/Heroku style URLs use postgres:// — SQLAlchemy needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

USING_SQLITE = DATABASE_URL.startswith("sqlite")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    # Comma-separated module permissions: aprec,filenamer,trends,payroll
    permissions = Column(String(255), default="aprec,filenamer,trends,payroll")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class GLFile(Base):
    __tablename__ = "gl_files"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    # 'shared' = the user's default GL; or a module override: aprec/trends/payroll
    scope = Column(String(16), nullable=False, default="shared")
    filename = Column(String(512), nullable=False)
    data_gz = Column(LargeBinary, nullable=False)      # gzip-compressed CSV bytes
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (UniqueConstraint("user_id", "scope", name="uq_gl_user_scope"),)


def init_db():
    Base.metadata.create_all(bind=engine)
    # Defensive migration: create_all doesn't ALTER existing tables, so add
    # the permissions column to a pre-existing users table if it's missing.
    from sqlalchemy import text
    try:
        with engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN permissions VARCHAR(255) "
                "DEFAULT 'aprec,filenamer,trends,payroll'"))
    except Exception:
        pass  # column already exists
    try:
        with engine.begin() as conn:
            conn.execute(text(
                "UPDATE users SET permissions = 'aprec,filenamer,trends,payroll' "
                "WHERE permissions IS NULL"))
    except Exception:
        pass
    # GL scope migration (safe to re-run)
    for stmt in (
        "ALTER TABLE gl_files ADD COLUMN scope VARCHAR(16) DEFAULT 'shared'",
        "UPDATE gl_files SET scope = 'shared' WHERE scope IS NULL",
        "ALTER TABLE gl_files DROP CONSTRAINT gl_files_user_id_key",       # postgres old unique
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_gl_user_scope ON gl_files (user_id, scope)",
    ):
        try:
            with engine.begin() as conn:
                conn.execute(text(stmt))
        except Exception:
            pass


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── GL helpers ─────────────────────────────────────────────────────────────
def store_gl(db, user_id: int, filename: str, csv_bytes: bytes, scope: str = "shared"):
    """Replace THIS USER's stored GL for the given scope. Strictly per-user."""
    row = (db.query(GLFile)
             .filter(GLFile.user_id == user_id, GLFile.scope == scope).first())
    gz = gzip.compress(csv_bytes)
    if row:
        row.filename = filename
        row.data_gz = gz
        row.uploaded_at = datetime.now(timezone.utc)
    else:
        row = GLFile(user_id=user_id, scope=scope, filename=filename, data_gz=gz)
        db.add(row)
    db.commit()
    return row


def load_gl(db, user_id: int, scope: str = None):
    """
    Return (filename, csv_bytes, uploaded_at, used_scope) for THIS USER only.
    With a module scope: prefer the module's own GL, else fall back to the
    user's shared GL. None if neither exists.
    """
    row = None
    if scope and scope != "shared":
        row = (db.query(GLFile)
                 .filter(GLFile.user_id == user_id, GLFile.scope == scope).first())
    if row is None:
        row = (db.query(GLFile)
                 .filter(GLFile.user_id == user_id, GLFile.scope == "shared").first())
    if not row:
        return None
    return row.filename, gzip.decompress(row.data_gz), row.uploaded_at, row.scope


def delete_gl(db, user_id: int, scope: str):
    """Remove THIS USER's module-specific GL (reverting the module to shared)."""
    n = (db.query(GLFile)
           .filter(GLFile.user_id == user_id, GLFile.scope == scope).delete())
    db.commit()
    return n


def gl_overview(db, user_id: int):
    """All GL slots for THIS USER: {scope: {filename, uploaded_at}}."""
    out = {}
    for row in db.query(GLFile).filter(GLFile.user_id == user_id).all():
        out[row.scope] = {"filename": row.filename, "uploaded_at": row.uploaded_at}
    return out
