from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from .exceptions import EmbeddingError

class Embedder:
    """Generates embeddings using a local SentenceTransformers model."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            raise EmbeddingError(f"Failed to load embedding model {model_name}: {e}")
            
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Returns normalized embeddings for cosine similarity."""
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embeddings: {e}")
            
    def embed_query(self, query: str) -> np.ndarray:
        return self.embed_texts([query])[0]
