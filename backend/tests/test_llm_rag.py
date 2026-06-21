import pytest
from unittest.mock import patch, MagicMock
from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

@patch("src.llm.gemini_client.GeminiClient.generate_content")
def test_llm_explain(mock_generate):
    # Setup mock to return a string response directly
    mock_generate.return_value = "Your transport emissions are high, but you can reduce them."

    payload = {
        "user_id": "test_user_01",
        "context_type": "footprint",
        "context_data": {"total_emissions_kg_co2e": 1500.0}
    }
    response = client.post("/api/v1/llm/explain", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "transport emissions are high" in data["data"]["explanation_text"]
    assert mock_generate.called

@patch("src.llm.gemini_client.GeminiClient.generate_content")
@patch("src.rag.rag_service.RAGService.query")
def test_rag_query(mock_rag_query, mock_generate):
    from src.rag.schemas import RetrievalResponse, RetrievalResult, Chunk, DocumentMetadata
    
    # Mock RAG retrieval
    mock_chunk = Chunk(
        id="123", 
        document_id="doc1", 
        text="Public transit emits 0.05 kg CO2e per mile.", 
        metadata=DocumentMetadata(source="epa.md", doc_type="md")
    )
    mock_rag_query.return_value = RetrievalResponse(
        results=[RetrievalResult(chunk=mock_chunk, score=0.9)],
        relevance=True,
        weak_context=False
    )
    
    # Mock Gemini generation (JSON string matching the expected schema)
    mock_generate.return_value = '{"answer": "Based on the documents, public transit is very efficient.", "grounded_facts": ["Public transit is efficient"], "suggested_follow_up_questions": []}'

    payload = {
        "user_id": "test_user_01",
        "query": "Is public transit efficient?"
    }
    response = client.post("/api/v1/rag/query", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "public transit" in data["data"]["answer"]
    assert "epa.md" in data["data"]["sources"]
