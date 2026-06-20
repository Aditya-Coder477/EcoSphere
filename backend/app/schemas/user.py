from pydantic import BaseModel, Field
from typing import Optional, Dict

class UserProfileCreate(BaseModel):
    user_id: str
    occupation: Optional[str] = "unknown"
    city_type: Optional[str] = "urban"
    budget_profile: Optional[str] = "medium"
    is_vegetarian: Optional[bool] = False
    
class UserProfileResponse(UserProfileCreate):
    pass
