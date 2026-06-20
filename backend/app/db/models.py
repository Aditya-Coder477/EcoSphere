"""
models.py
=========
SQLAlchemy models.
"""

import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, JSON
from .session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    
    # Profile context
    occupation = Column(String)
    city_type = Column(String)
    budget_profile = Column(String)
    is_vegetarian = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
class CarbonProfile(Base):
    __tablename__ = "carbon_profiles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, index=True)
    
    # Stored as JSON for simplicity
    category_emissions = Column(JSON)
    total_emissions_kg_co2e = Column(Float)
    dominant_emission_source = Column(String)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, index=True)
    
    action_id = Column(String, index=True)
    category = Column(String)
    impact_score = Column(Float)
    impact_level = Column(String)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
