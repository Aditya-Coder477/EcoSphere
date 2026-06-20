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
    
    # DB
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./carbon_platform.db"  # Default to local SQLite
    )
    
    # Security placeholders
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        case_sensitive = True

settings = Settings()
