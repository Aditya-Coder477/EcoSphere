import os
import json
import numpy as np
import faiss
from pathlib import Path
from typing import List, Dict, Optional
from .schemas import Chunk
from .exceptions import RAGError

class VectorStoreManager:
    """Manages FAISS index and chunk metadata for similarity search."""
    
    def __init__(self, dimension: int = 384, index_path: Optional[str] = None):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension) # Inner product for cosine similarity (if normalized)
        self.chunks: Dict[int, Chunk] = {} # Map faiss ID to Chunk
        self.current_id = 0
        
        if index_path:
            self.load_index(index_path)
            
    def add_chunks(self, chunks: List[Chunk], embeddings: np.ndarray):
        if len(chunks) != embeddings.shape[0]:
            raise RAGError("Number of chunks must match number of embeddings.")
            
        if embeddings.shape[1] != self.dimension:
            raise RAGError(f"Embeddings dimension {embeddings.shape[1]} does not match index dimension {self.dimension}")
            
        self.index.add(embeddings)
        
        for i, chunk in enumerate(chunks):
            self.chunks[self.current_id] = chunk
            self.current_id += 1
            
    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[tuple[Chunk, float]]:
        if self.index.ntotal == 0:
            return []
            
        # faiss expects 2D array
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
            
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for j, idx in enumerate(indices[0]):
            if idx != -1 and idx in self.chunks: # -1 means not enough results
                results.append((self.chunks[idx], float(scores[0][j])))
        return results
        
    def save_index(self, directory: str | Path):
        """Persists the FAISS index and metadata to disk."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        
        faiss.write_index(self.index, str(directory / "faiss.index"))
        
        # Save chunks map
        chunks_data = {
            k: chunk.model_dump() for k, chunk in self.chunks.items()
        }
        with open(directory / "chunks.json", "w", encoding="utf-8") as f:
            json.dump(chunks_data, f)
            
        with open(directory / "metadata.json", "w", encoding="utf-8") as f:
            json.dump({"dimension": self.dimension, "current_id": self.current_id}, f)
            
    def load_index(self, directory: str | Path):
        """Loads the FAISS index and metadata from disk."""
        directory = Path(directory)
        index_file = directory / "faiss.index"
        chunks_file = directory / "chunks.json"
        meta_file = directory / "metadata.json"
        
        if not index_file.exists() or not chunks_file.exists():
            return # Start fresh if not found
            
        self.index = faiss.read_index(str(index_file))
        
        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks_data = json.load(f)
            self.chunks = {int(k): Chunk(**v) for k, v in chunks_data.items()}
            
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
            self.dimension = meta["dimension"]
            self.current_id = meta["current_id"]
