"""
session.py
==========
SQLAlchemy session setup.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.app.core.config import settings

import logging

log = logging.getLogger(__name__)

# check_same_thread is a SQLite-only argument — not valid for PostgreSQL
db_url = settings.SQLALCHEMY_DATABASE_URI
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

try:
    engine = create_engine(db_url, connect_args=connect_args)
    if not db_url.startswith("sqlite"):
        # Verify connectivity — log only scheme+host, never credentials
        try:
            from urllib.parse import urlparse
            _parsed = urlparse(db_url)
            _safe_url = f"{_parsed.scheme}://{_parsed.hostname}"
        except Exception:
            _safe_url = "<database>"
        with engine.connect() as conn:
            pass
        log.info("Database connected successfully: %s", _safe_url)
except Exception as e:
    log.error("Database connection failed (credentials redacted): %s. Falling back to local SQLite database.", type(e).__name__)
    db_url = "sqlite:///./carbon_platform.db"
    connect_args = {"check_same_thread": False}
    engine = create_engine(db_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
