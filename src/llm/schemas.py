from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ExplanationRequest(BaseModel):
    user_id: str
    context_type: str # "footprint", "recommendation", "rag_qa"
    context_data: Dict[str, Any]
    query: Optional[str] = None
    tone: str = "friendly" # "friendly", "technical", "concise", "detailed"

class SourceCitation(BaseModel):
    source: str
    chunk_text: str

class ExplanationResponse(BaseModel):
    explanation_text: str
    model_used: str
    sources: Optional[List[SourceCitation]] = None
    confidence: str = "medium"
    fallback_mode: str = "none"
    response_source: str = "demo"
    suggested_follow_up_questions: List[str] = []
    used_demo_data: bool = False
    grounded_facts: List[str] = []

class ClimateCoachSummaryRequest(BaseModel):
    user_id: str
    total_emissions: float
    dominant_category: str
    recommendations: List[Dict[str, Any]]
    tone: str = "friendly"
