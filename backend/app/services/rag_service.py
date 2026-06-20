"""
rag_service.py
==============
Integrates with src.rag.
"""

from backend.app.schemas.llm import RAGQueryRequest, RAGQueryResponse
from src.llm import ExplanationService, ExplanationRequest
from src.rag import RAGService

from sqlalchemy.orm import Session

_rag_service = RAGService()

def execute_query(request: RAGQueryRequest, db: Session = None) -> RAGQueryResponse:
    """
    Calls the src.llm module for knowledge retrieval and explanation.
    """
    service = ExplanationService(rag_service=_rag_service, db=db)
    
    req = ExplanationRequest(
        user_id=request.user_id,
        context_type="rag_qa",
        context_data={},
        query=request.query
    )
    
    res = service.generate_explanation(req)
    
    sources = [s.source for s in res.sources] if res.sources else []
    
    return RAGQueryResponse(
        answer=res.explanation_text,
        sources=sources,
        confidence=res.confidence,
        fallback_mode=res.fallback_mode,
        response_source=res.response_source,
        suggested_follow_up_questions=res.suggested_follow_up_questions,
        used_demo_data=res.used_demo_data,
        grounded_facts=res.grounded_facts
    )
