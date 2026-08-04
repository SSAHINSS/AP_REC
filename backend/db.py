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

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer,
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
                     unique=True, nullable=False, index=True)
    filename = Column(String(512), nullable=False)
    data_gz = Column(LargeBinary, nullable=False)      # gzip-compressed CSV bytes
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


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


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── GL helpers ─────────────────────────────────────────────────────────────
def store_gl(db, user_id: int, filename: str, csv_bytes: bytes):
    """Replace the user's stored GL with a new upload."""
    row = db.query(GLFile).filter(GLFile.user_id == user_id).first()
    gz = gzip.compress(csv_bytes)
    if row:
        row.filename = filename
        row.data_gz = gz
        row.uploaded_at = datetime.now(timezone.utc)
    else:
        row = GLFile(user_id=user_id, filename=filename, data_gz=gz)
        db.add(row)
    db.commit()
    return row


def load_gl(db, user_id: int):
    """Return (filename, csv_bytes, uploaded_at) or None if nothing stored."""
    row = db.query(GLFile).filter(GLFile.user_id == user_id).first()
    if not row:
        return None
    return row.filename, gzip.decompress(row.data_gz), row.uploaded_at
