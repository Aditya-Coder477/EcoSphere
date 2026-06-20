class LLMError(Exception):
    """Base exception for LLM operations."""
    pass

class GeminiAPIError(LLMError):
    """Raised when the Gemini API call fails."""
    pass

class ContextMissingError(LLMError):
    """Raised when RAG context is insufficient to answer the query."""
    pass
