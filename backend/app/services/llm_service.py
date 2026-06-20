"""
llm_service.py
==============
Integrates with src.llm.
"""

from backend.app.schemas.llm import LLMExplanationRequest, LLMExplanationResponse
from src.llm import ExplanationService, ExplanationRequest
from src.rag import RAGService

# Instantiate a global rag service to share the index
_rag_service = RAGService()
_rag_service.build_index()

def generate_explanation(request: LLMExplanationRequest) -> LLMExplanationResponse:
    """
    Calls the src.llm module to generate natural language explanations.
    """
    service = ExplanationService(rag_service=_rag_service)
    
    req = ExplanationRequest(
        user_id=request.user_id,
        context_type=request.context_type,
        context_data=request.context_data
    )
    
    res = service.generate_explanation(req)
    
    return LLMExplanationResponse(
        explanation_text=res.explanation_text,
        model_used=res.model_used
    )
