"""
crud.py
=======
DB access utilities.
"""

from sqlalchemy.orm import Session
from typing import Dict, Any

from . import models

def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user_id: str, profile_data: Dict[str, Any]):
    db_user = models.User(
        id=user_id,
        occupation=profile_data.get("occupation", ""),
        city_type=profile_data.get("city_type", ""),
        budget_profile=profile_data.get("budget_profile", "medium"),
        is_vegetarian=profile_data.get("is_vegetarian", False)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def save_carbon_profile(db: Session, user_id: str, emissions: dict, total: float, dominant: str):
    profile = models.CarbonProfile(
        user_id=user_id,
        category_emissions=emissions,
        total_emissions_kg_co2e=total,
        dominant_emission_source=dominant
    )
    db.add(profile)
    db.commit()
    return profile

def save_recommendation_history(db: Session, user_id: str, recommendations: list):
    for rec in recommendations:
        history = models.RecommendationHistory(
            user_id=user_id,
            action_id=rec.action_id,
            category=rec.category,
            impact_score=rec.impact_score,
            impact_level=rec.impact_level
        )
        db.add(history)
    db.commit()
