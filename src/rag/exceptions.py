class RAGError(Exception):
    """Base exception for RAG operations."""
    pass

class EmptyIndexError(RAGError):
    """Raised when querying an empty vector store index."""
    pass

class DocumentLoadError(RAGError):
    """Raised when a document cannot be loaded."""
    pass

class EmbeddingError(RAGError):
    """Raised when an error occurs during embedding generation."""
    pass
