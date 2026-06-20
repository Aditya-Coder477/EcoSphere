"""
tests/test_assistant_fallback.py
================================
Tests for the Climate Coach robust fallback mechanism.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.llm import ExplanationService, ExplanationRequest
from src.llm.schemas import ExplanationResponse
from src.rag import RAGService
from src.rag.schemas import RetrievalResponse, RetrievalResult, Chunk, DocumentMetadata


@pytest.fixture
def mock_rag_service():
    """Returns a mocked RAGService."""
    service = MagicMock(spec=RAGService)
    return service


def test_vague_query_clarification(mock_rag_service):
    """Ensure vague queries trigger clarification mode and low confidence."""
    service = ExplanationService(rag_service=mock_rag_service)
    
    # We mock GeminiClient to return a JSON clarification string
    mock_response = (
        '{"answer": "Would you like to talk about transport, food, or electricity?", '
        '"grounded_facts": [], "suggested_follow_up_questions": ["Option A", "Option B"]}'
    )
    
    with patch.object(service.client, "generate_content", return_value=mock_response) as mock_gen:
        req = ExplanationRequest(
            user_id="test_user",
            context_type="rag_qa",
            context_data={},
            query="hi"
        )
        res = service.generate_explanation(req)
        
        # Verify call parameters
        assert res.fallback_mode == "clarification"
        assert res.response_source == "clarification"
        assert res.confidence == "low"
        assert res.used_demo_data is False
        assert "transport" in res.explanation_text
        assert len(res.suggested_follow_up_questions) == 2


def test_strong_rag_grounded_response(mock_rag_service):
    """Ensure high score RAG match results in grounded_answer/rag response_source and high confidence."""
    service = ExplanationService(rag_service=mock_rag_service)
    
    # Create a mock high score result (score = 0.85 >= 0.70)
    meta = DocumentMetadata(source="epa.md", doc_type="guideline")
    chunk = Chunk(id="c1", document_id="d1", text="Driving cars emits 0.404 kg/mile.", metadata=meta)
    high_score_result = RetrievalResult(chunk=chunk, score=0.85)
    
    mock_rag_service.query.return_value = RetrievalResponse(
        results=[high_score_result],
        relevance=True,
        weak_context=False
    )
    
    mock_response = (
        '{"answer": "Based on the EPA guidelines, driving passenger cars contributes approximately 0.404 kg CO2e.", '
        '"grounded_facts": ["Cars emit 0.404 kg/mile"], "suggested_follow_up_questions": []}'
    )
    
    # Mock DB query to return real user data so used_demo_data is False
    with patch.object(service, "_get_user_facts", return_value=({"profile": {"user_id": "test_user"}}, False)):
        with patch.object(service.client, "generate_content", return_value=mock_response):
            req = ExplanationRequest(
                user_id="test_user",
                context_type="rag_qa",
                context_data={},
                query="What are car emissions?"
            )
            res = service.generate_explanation(req)
            
            assert res.confidence == "high"
            assert res.fallback_mode == "none"
            assert res.response_source == "rag_profile"
            assert res.used_demo_data is False
            assert "0.404" in res.explanation_text


def test_weak_rag_fallback_response(mock_rag_service):
    """Ensure weak RAG match (score < 0.60) triggers fallback mode and falls back to user facts."""
    service = ExplanationService(rag_service=mock_rag_service)
    
    # Create a mock low score result (score = 0.45 < 0.60)
    meta = DocumentMetadata(source="epa.md", doc_type="guideline")
    chunk = Chunk(id="c1", document_id="d1", text="Some irrelevant info about wind turbines.", metadata=meta)
    low_score_result = RetrievalResult(chunk=chunk, score=0.45)
    
    mock_rag_service.query.return_value = RetrievalResponse(
        results=[low_score_result],
        relevance=False,
        weak_context=True
    )
    
    mock_response = (
        '{"answer": "Your footprint is 7240 kg, dominated by transport. You should try public transit.", '
        '"grounded_facts": ["Dominant source is transport"], "suggested_follow_up_questions": ["How do I save?"]}'
    )
    
    # Mock DB lookup to return mock user data so used_demo_data is True
    with patch.object(service, "_get_user_facts", return_value=({"profile": {}}, True)):
        with patch.object(service.client, "generate_content", return_value=mock_response):
            req = ExplanationRequest(
                user_id="demo_user",
                context_type="rag_qa",
                context_data={},
                query="How can I save?"
            )
            res = service.generate_explanation(req)
            
            assert res.confidence == "low" # weak score (<0.50) + demo data
            assert res.fallback_mode == "demo"
            assert res.response_source == "demo"
            assert res.used_demo_data is True
            assert "7240" in res.explanation_text


def test_missing_data_demo_fallback(mock_rag_service):
    """Ensure that completely missing database records fallback to demo data automatically."""
    service = ExplanationService(rag_service=mock_rag_service)
    
    mock_rag_service.query.return_value = RetrievalResponse(
        results=[],
        relevance=False,
        weak_context=True
    )
    
    mock_response = (
        '{"answer": "Using simulated details, we see transport is your biggest category.", '
        '"grounded_facts": ["Using mock data"], "suggested_follow_up_questions": []}'
    )
    
    # We do NOT patch _get_user_facts, letting it hit the ad-hoc SessionLocal fallback
    # which fails or returns empty, triggering mock/demo context.
    with patch.object(service.client, "generate_content", return_value=mock_response):
        req = ExplanationRequest(
            user_id="completely_new_id_not_in_db",
            context_type="rag_qa",
            context_data={},
            query="Tell me about my footprint"
        )
        res = service.generate_explanation(req)
        
        assert res.used_demo_data is True
        assert res.fallback_mode == "demo"
        assert res.response_source == "demo"
        assert res.confidence == "low" # no RAG chunks + demo data
        assert "simulated" in res.explanation_text
