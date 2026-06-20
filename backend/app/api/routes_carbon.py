from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.app.db.session import get_db
from backend.app.db import crud
from backend.app.schemas.carbon import CarbonCalculationRequest, CarbonCalculationResponse
from backend.app.services import carbon_service
from backend.app.utils.response_helpers import success_response

router = APIRouter()

@router.post("/calculate", response_model=Dict[str, Any])
async def calculate_carbon(request: CarbonCalculationRequest, db: Session = Depends(get_db)):
    """Calculates carbon footprint from raw activities."""
    # 1. Orchestrate the calculation
    result: CarbonCalculationResponse = carbon_service.calculate_footprint(request)
    
    # 2. Persist profile
    crud.save_carbon_profile(
        db=db,
        user_id=request.user_id,
        emissions=result.category_emissions,
        total=result.total_emissions_kg_co2e,
        dominant=result.dominant_source
    )
    
    # 3. Return Standard Response
    return success_response(data=result.model_dump(), message="Footprint calculated successfully")
