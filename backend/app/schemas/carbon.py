from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class TransportActivity(BaseModel):
    mode: str
    distance_km: float

class FoodActivity(BaseModel):
    food_item: str
    quantity_kg: float
    
class ElectricityActivity(BaseModel):
    country: str
    kwh_per_month: Optional[float] = None

class WasteActivity(BaseModel):
    country: str
    waste_generated_kg_per_day: Optional[float] = None

class CarbonCalculationRequest(BaseModel):
    user_id: str
    transport: Optional[List[TransportActivity]] = None
    food: Optional[List[FoodActivity]] = None
    electricity: Optional[ElectricityActivity] = None
    waste: Optional[WasteActivity] = None

class CarbonCalculationResponse(BaseModel):
    user_id: str
    total_emissions_kg_co2e: float
    category_emissions: Dict[str, float]
    category_shares_pct: Dict[str, float]
    dominant_source: str
    human_readable_summary: str
