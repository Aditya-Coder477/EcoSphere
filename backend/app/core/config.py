"""
config.py
=========
Backend configuration settings using Pydantic BaseSettings.
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Carbon Footprint Platform API"
    API_V1_STR: str = "/api/v1"
    
    # DB: Self-heal common environment variable and copy-paste errors
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        db_url = os.getenv("DATABASE_URL", "sqlite:///./carbon_platform.db")
        if db_url:
            db_url = db_url.strip().strip("'\"")
            # If it starts with legacy 'postgres://', replace with 'postgresql://' (required by SQLAlchemy 2.0)
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            # If the protocol scheme is missing (e.g., copy-pasted Neon host starting with username@)
            elif "://" not in db_url and "@" in db_url:
                db_url = "postgresql://" + db_url
            
            # Self-heal copy-paste errors for Neon where password is treated as username (no password supplied)
            # e.g., postgresql://npg_ZEQXL8PD7RYS@ep-host... -> postgresql://neondb_owner:npg_ZEQXL8PD7RYS@ep-host...
            if db_url.startswith("postgresql://"):
                try:
                    from urllib.parse import urlparse, urlunparse
                    parsed = urlparse(db_url)
                    if parsed.username and parsed.username.startswith("npg_") and not parsed.password:
                        new_netloc = f"neondb_owner:{parsed.username}@{parsed.hostname}"
                        if parsed.port:
                            new_netloc += f":{parsed.port}"
                        db_url = urlunparse((
                            parsed.scheme,
                            new_netloc,
                            parsed.path,
                            parsed.params,
                            parsed.query,
                            parsed.fragment
                        ))
                except Exception:
                    pass
        return db_url
    
    # Security placeholders
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        case_sensitive = True

settings = Settings()
