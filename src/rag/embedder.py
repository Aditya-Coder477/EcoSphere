from typing import List, Union, Optional
import os
import numpy as np
from google import genai
from .exceptions import EmbeddingError
from src.utils.logger import get_logger

log = get_logger(__name__)

class Embedder:
    """Generates embeddings using Google Gemini's API instead of a local PyTorch model."""
    
    def __init__(self, model_name: str = "text-embedding-004"):
        self.model_name = model_name
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                log.warning(f"Failed to initialize Gemini Client for Embeddings: {e}")

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Returns normalized embeddings from Gemini API. Fallback to random unit vectors if offline."""
        # Try initializing client if it wasn't done on startup
        if not self.client:
            self.api_key = os.environ.get("GEMINI_API_KEY")
            if self.api_key:
                try:
                    self.client = genai.Client(api_key=self.api_key)
                except Exception:
                    pass
        
        # If still no client/api_key, fallback to mock normalized embeddings (dimension 768)
        if not self.client:
            log.warning("No GEMINI_API_KEY set. Falling back to simulated 768-dimensional embeddings.")
            rng = np.random.default_rng(seed=42)
            mock_embeddings = rng.standard_normal((len(texts), 768))
            norms = np.linalg.norm(mock_embeddings, axis=1, keepdims=True)
            return (mock_embeddings / np.maximum(norms, 1e-9)).astype(np.float32)
            
        try:
            log.debug(f"Calling Gemini API to embed {len(texts)} texts...")
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=texts
            )
            
            # Extract embedding vectors
            embeddings_list = [e.values for e in response.embeddings]
            embs = np.array(embeddings_list, dtype=np.float32)
            
            # Normalize them for cosine similarity search (faiss IndexFlatIP uses dot product)
            norms = np.linalg.norm(embs, axis=1, keepdims=True)
            return embs / np.maximum(norms, 1e-9)
            
        except Exception as e:
            log.error(f"Gemini Embeddings API call failed: {e}. Falling back to simulated embeddings.")
            rng = np.random.default_rng(seed=42)
            mock_embeddings = rng.standard_normal((len(texts), 768))
            norms = np.linalg.norm(mock_embeddings, axis=1, keepdims=True)
            return (mock_embeddings / np.maximum(norms, 1e-9)).astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed_texts([query])[0]
