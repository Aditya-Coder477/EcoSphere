"""
backend/tests/conftest.py
=========================
Shared fixtures and automatic mocks for the backend test suite.
"""

import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_gemini_client():
    """
    Automatically mock the generate_content method of GeminiClient
    to prevent real network calls to the Gemini API during backend tests.
    """
    with patch("src.llm.gemini_client.GeminiClient.generate_content") as mock_gen:
        # Default mock response for a general question
        mock_gen.return_value = "This is a mock explanation from the AI Climate Coach."
        
        # If the call is for a RAG query or footprint explanation, customize the response dynamically
        def side_effect(prompt, *args, **kwargs):
            prompt_str = str(prompt)
            # RAG/QA query expecting JSON
            if "JSON" in prompt_str or "json" in prompt_str.lower() or kwargs.get("response_mime_type") == "application/json":
                # Check for query topic
                answer = "Based on the mock documents, this is a mock RAG response."
                if "transit" in prompt_str.lower() or "transit" in kwargs.get("response_mime_type", "").lower():
                    answer = "Based on the mock documents, public transit is efficient and better."
                return f'{{"answer": "{answer}", "grounded_facts": ["Mock fact 1"], "suggested_follow_up_questions": ["Question A"]}}'
            
            # General explanation
            explanation = "This is a mock explanation from the AI Climate Coach."
            if "1500" in prompt_str:
                explanation = "This is a mock explanation from the AI Climate Coach with total emissions 1500.0 kg."
            return explanation
            
        mock_gen.side_effect = side_effect
        yield mock_gen
