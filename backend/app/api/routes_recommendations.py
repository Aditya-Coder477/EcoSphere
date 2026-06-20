from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.app.db.session import get_db
from backend.app.db import crud
from backend.app.schemas.recommendation import RecommendationRequest
from backend.app.services import recommendation_service
from backend.app.utils.response_helpers import success_response

router = APIRouter()

@router.post("/", response_model=Dict[str, Any])
async def get_recommendations(request: RecommendationRequest, top_n: int = 3, db: Session = Depends(get_db)):
    """Generates ranked carbon reduction recommendations based on a footprint profile."""
    # 1. Orchestrate ranking
    result = recommendation_service.generate_recommendations(request, top_n=top_n)
    
    # 2. Persist history
    crud.save_recommendation_history(
        db=db,
        user_id=request.user_id,
        recommendations=result.recommendations
    )
    
    return success_response(data=result.model_dump(), message="Recommendations generated")
