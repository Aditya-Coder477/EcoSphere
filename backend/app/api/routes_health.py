from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "service": "Carbon Footprint Platform API"}

@router.get("/metadata")
async def get_metadata():
    """Returns application metadata."""
    return {
        "version": "1.0.0",
        "datasets": {
            "emission_factors": "2025.1",
            "country_mix": "2024.3"
        },
        "last_updated": "2026-06-20T00:00:00Z"
    }
