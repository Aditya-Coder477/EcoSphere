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
        with engine.connect() as conn:
            pass
except Exception as e:
    log.error(f"Database connection failed: {e}. Falling back to local SQLite database.")
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
