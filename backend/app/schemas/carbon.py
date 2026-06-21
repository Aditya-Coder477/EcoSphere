"""
carbon.py
=========
Pydantic request/response schemas for the carbon calculation API.
All numeric fields are validated at the boundary so the engine always
receives clean, non-negative inputs.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class TransportActivity(BaseModel):
    mode: str = Field(..., min_length=1, max_length=100, description="Transport mode, e.g. 'Car', 'Bus'")
    distance_km: float = Field(..., ge=0, le=100_000, description="Distance in kilometres (≥ 0)")

    @field_validator("mode")
    @classmethod
    def _strip_mode(cls, v: str) -> str:
        return v.strip()


class FoodActivity(BaseModel):
    food_item: str = Field(..., min_length=1, max_length=200, description="Food item name")
    quantity_kg: float = Field(..., ge=0, le=10_000, description="Quantity in kilograms (≥ 0)")

    @field_validator("food_item")
    @classmethod
    def _strip_food_item(cls, v: str) -> str:
        return v.strip()


class ElectricityActivity(BaseModel):
    country: str = Field(..., min_length=1, max_length=100, description="Country name")
    kwh_per_month: Optional[float] = Field(
        None, ge=0, le=100_000,
        description="Monthly electricity consumption in kWh. If omitted, falls back to country average."
    )


class WasteActivity(BaseModel):
    country: str = Field(..., min_length=1, max_length=100, description="Country name")
    waste_generated_kg_per_day: Optional[float] = Field(
        None, ge=0, le=1_000,
        description="Daily waste generated in kg. If omitted, falls back to country average."
    )


class CarbonCalculationRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128, description="Unique user identifier")
    transport: Optional[List[TransportActivity]] = Field(None, max_length=50)
    food: Optional[List[FoodActivity]] = Field(None, max_length=200)
    electricity: Optional[ElectricityActivity] = None
    waste: Optional[WasteActivity] = None


class CarbonCalculationResponse(BaseModel):
    user_id: str
    total_emissions_kg_co2e: float
    category_emissions: dict[str, float]
    category_shares_pct: dict[str, float]
    dominant_source: str
    human_readable_summary: str

