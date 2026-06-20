from pydantic import BaseModel
from typing import Dict, Any

class LLMExplanationRequest(BaseModel):
    user_id: str
    context_type: str # "footprint" or "recommendation"
    context_data: Dict[str, Any]

class LLMExplanationResponse(BaseModel):
    explanation_text: str
    model_used: str

class RAGQueryRequest(BaseModel):
    user_id: str
    query: str
    context_filter: str = ""

class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: str
    fallback_mode: str
    response_source: str
    suggested_follow_up_questions: list[str]
    used_demo_data: bool
    grounded_facts: list[str]
