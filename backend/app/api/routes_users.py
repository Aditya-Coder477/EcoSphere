from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.app.db.session import get_db
from backend.app.schemas.user import UserProfileCreate, UserProfileResponse
from backend.app.services import user_service
from backend.app.utils.response_helpers import success_response, error_response

router = APIRouter()

@router.post("/", response_model=Dict[str, Any])
async def create_user(user_in: UserProfileCreate, db: Session = Depends(get_db)):
    """Creates or updates a user profile."""
    user = user_service.create_or_update_user(db, user_in)
    return success_response(data={"user_id": user.id}, message="User created successfully")

@router.get("/{user_id}", response_model=Dict[str, Any])
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Fetches a user profile."""
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    data = {
        "user_id": user.id,
        "occupation": user.occupation,
        "city_type": user.city_type,
        "budget_profile": user.budget_profile,
        "is_vegetarian": user.is_vegetarian
    }
    return success_response(data=data)
