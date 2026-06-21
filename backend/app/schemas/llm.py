"""
llm.py
======
Pydantic schemas for LLM explanation and RAG query API endpoints.
Input fields are length-bounded to prevent empty or oversized requests.
"""

from pydantic import BaseModel, Field

_MAX_QUERY_LENGTH: int = 2_000   # Characters — prevents prompt injection via huge inputs
_MAX_CONTEXT_TYPE_LENGTH: int = 50


class LLMExplanationRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    context_type: str = Field(
        ..., min_length=1, max_length=_MAX_CONTEXT_TYPE_LENGTH,
        description="One of: 'footprint', 'recommendation'"
    )
    context_data: dict = Field(..., description="Serialised footprint or recommendation payload")


class LLMExplanationResponse(BaseModel):
    explanation_text: str
    model_used: str


class RAGQueryRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    query: str = Field(..., min_length=1, max_length=_MAX_QUERY_LENGTH, description="User's natural-language question")
    context_filter: str = Field("", max_length=100)


class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: str
    fallback_mode: str
    response_source: str
    suggested_follow_up_questions: list[str]
    used_demo_data: bool
    grounded_facts: list[str]

