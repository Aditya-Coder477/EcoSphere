"""
config.py
=========
Backend configuration settings using Pydantic BaseSettings.

Security notes
--------------
* SECRET_KEY  – Must be at least 32 characters in production. Set the
  ``SECRET_KEY`` environment variable to a securely generated random string.
  The insecure placeholder "changeme" is rejected outside development mode.
* BACKEND_CORS_ORIGINS – Set the ``BACKEND_CORS_ORIGINS`` env var to a
  comma-separated list of allowed origins, e.g.
  ``https://app.ecosphere.io,https://staging.ecosphere.io``.
  Defaults to localhost only so that the server cannot be called from
  arbitrary origins in production.
"""

import os
import logging

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings

log = logging.getLogger(__name__)

_INSECURE_SECRETS: frozenset[str] = frozenset(
    {"changeme", "secret", "password", "dev", "test", "insecure", ""}
)


def _parse_cors_origins(raw: str) -> list[str]:
    """Split a comma-separated CORS origins string into a validated list."""
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    return origins if origins else ["http://localhost:5173", "http://localhost:3000"]


class Settings(BaseSettings):
    PROJECT_NAME: str = "Carbon Footprint Platform API"
    API_V1_STR: str = "/api/v1"

    # ------------------------------------------------------------------ #
    # Database                                                             #
    # ------------------------------------------------------------------ #
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Return a sanitised, SQLAlchemy-compatible database URL.

        Applies self-healing transformations for common copy-paste mistakes
        when using Neon PostgreSQL connection strings.
        """
        db_url = os.getenv("DATABASE_URL", "sqlite:///./carbon_platform.db")
        if db_url:
            db_url = db_url.strip().strip("'\"")
            # Legacy postgres:// -> postgresql:// (required by SQLAlchemy 2.0)
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            # Missing scheme entirely (bare host@...)
            elif "://" not in db_url and "@" in db_url:
                db_url = "postgresql://" + db_url

            # Self-heal Neon copy-paste: password mistakenly placed as username
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
                            parsed.fragment,
                        ))
                except Exception:
                    pass
        return db_url

    # ------------------------------------------------------------------ #
    # Security                                                             #
    # ------------------------------------------------------------------ #
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme-replace-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    @field_validator("SECRET_KEY")
    @classmethod
    def _validate_secret_key(cls, v: str) -> str:
        """Reject obviously insecure SECRET_KEY values in non-development environments."""
        is_dev = os.getenv("APP_ENV", "development").lower() in {"development", "dev", "test"}
        if not is_dev and (v.lower() in _INSECURE_SECRETS or len(v) < 32):
            raise ValueError(
                "SECRET_KEY is insecure. Set a randomly generated string of "
                "at least 32 characters via the SECRET_KEY environment variable."
            )
        if v.lower() in _INSECURE_SECRETS:
            log.warning(
                "SECRET_KEY is using an insecure placeholder. "
                "Set a strong SECRET_KEY before deploying to production."
            )
        return v

    # ------------------------------------------------------------------ #
    # CORS                                                                 #
    # ------------------------------------------------------------------ #
    # Read from env: BACKEND_CORS_ORIGINS="https://app.eco.io,https://staging.eco.io"
    # Defaults to local dev origins.  "*" is accepted for local development
    # but will NOT be combined with allow_credentials=True (see main.py).
    BACKEND_CORS_ORIGINS: list[str] = _parse_cors_origins(
        os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    )

    class Config:
        case_sensitive = True


settings = Settings()

