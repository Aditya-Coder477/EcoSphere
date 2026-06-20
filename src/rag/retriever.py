from typing import List, Optional
from .embedder import Embedder
from .vector_store import VectorStoreManager
from .schemas import RetrievalResult, RetrievalResponse

class Retriever:
    """Retrieves relevant chunks for a given query."""
    
    def __init__(self, embedder: Embedder, vector_store: VectorStoreManager):
        self.embedder = embedder
        self.vector_store = vector_store
        
    def retrieve(self, query: str, top_k: int = 3, min_score: float = 0.0, similarity_threshold: float = 0.60) -> RetrievalResponse:
        query_embedding = self.embedder.embed_query(query)
        raw_results = self.vector_store.search(query_embedding, top_k=top_k)
        
        results = []
        for chunk, score in raw_results:
            if score >= min_score:
                results.append(RetrievalResult(chunk=chunk, score=score))
                
        relevance = any(r.score >= similarity_threshold for r in results) if results else False
        weak_context = not relevance
        
        return RetrievalResponse(
            results=results,
            relevance=relevance,
            weak_context=weak_context
        )
