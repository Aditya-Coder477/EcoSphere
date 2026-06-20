from fastapi import APIRouter, Depends
from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.llm import LLMExplanationRequest, RAGQueryRequest
from backend.app.services import llm_service, rag_service
from backend.app.utils.response_helpers import success_response

router_llm = APIRouter()
router_rag = APIRouter()

@router_llm.post("/explain", response_model=Dict[str, Any])
async def explain_data(request: LLMExplanationRequest):
    """Generates a natural language explanation of footprint or recommendation data."""
    result = llm_service.generate_explanation(request)
    return success_response(data=result.model_dump(), message="Explanation generated")

@router_rag.post("/query", response_model=Dict[str, Any])
async def query_knowledge_base(request: RAGQueryRequest, db: Session = Depends(get_db)):
    """Retrieves an answer from the carbon knowledge base."""
    result = rag_service.execute_query(request, db=db)
    return success_response(data=result.model_dump(), message="Query executed")
