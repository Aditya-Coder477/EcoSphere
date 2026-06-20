"""
user_service.py
===============
Service for user operations.
"""

from sqlalchemy.orm import Session
from backend.app.db import crud
from backend.app.schemas.user import UserProfileCreate

def create_or_update_user(db: Session, user_data: UserProfileCreate):
    # For now just checking if exists
    user = crud.get_user(db, user_data.user_id)
    if not user:
        user = crud.create_user(db, user_data.user_id, user_data.model_dump())
    # In a full app we'd update if it exists
    return user

def get_user(db: Session, user_id: str):
    return crud.get_user(db, user_id)
