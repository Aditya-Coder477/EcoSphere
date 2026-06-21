from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from backend.app.core.config import settings
from backend.app.core.exceptions import BaseAPIException
from backend.app.core.logging import logger
from backend.app.db.session import engine, Base

from backend.app.api.routes_health import router as health_router
from backend.app.api.routes_users import router as users_router
from backend.app.api.routes_carbon import router as carbon_router
from backend.app.api.routes_recommendations import router as recs_router
from backend.app.api.routes_llm import router_llm, router_rag

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS middleware
# ---------------------------------------------------------------------------
# Security: allow_credentials=True is incompatible with allow_origins=["*"]
# per the Fetch spec and browser enforcement. When origins is the wildcard we
# must set allow_credentials=False to avoid browsers blocking preflight.
_cors_wildcard = settings.BACKEND_CORS_ORIGINS == ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=not _cors_wildcard,  # False for wildcard, True for explicit origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)

logger.info(
    "CORS configured | origins=%s | credentials=%s",
    settings.BACKEND_CORS_ORIGINS,
    not _cors_wildcard,
)

# Timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} completed in {process_time:.4f}s")
    return response

# Global exception handler
@app.exception_handler(BaseAPIException)
async def custom_exception_handler(request: Request, exc: BaseAPIException):
    logger.error(f"API Error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "data": {}
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal Server Error",
            "data": {}
        }
    )

# Include routers
app.include_router(health_router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(carbon_router, prefix=f"{settings.API_V1_STR}/carbon", tags=["carbon"])
app.include_router(recs_router, prefix=f"{settings.API_V1_STR}/recommendations", tags=["recommendations"])
app.include_router(router_llm, prefix=f"{settings.API_V1_STR}/llm", tags=["llm"])
app.include_router(router_rag, prefix=f"{settings.API_V1_STR}/rag", tags=["rag"])
