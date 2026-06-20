import os
from pathlib import Path
from typing import List

from .document_loader import DocumentLoader
from .chunker import Chunker
from .embedder import Embedder
from .vector_store import VectorStoreManager
from .retriever import Retriever
from .schemas import RetrievalResult, RetrievalResponse
from src.utils.logger import get_logger

log = get_logger(__name__)

class RAGService:
    """Orchestrates the entire RAG pipeline."""
    
    def __init__(self, kb_dir: str = "knowledge_base", index_dir: str = ".rag_index"):
        self.kb_dir = Path(kb_dir)
        self.index_dir = Path(index_dir)
        
        self.embedder = Embedder()
        self.vector_store = VectorStoreManager(index_path=self.index_dir)
        self.retriever = Retriever(self.embedder, self.vector_store)
        
    def build_index(self, force_rebuild: bool = False):
        """Loads documents, chunks, embeds, and saves to index."""
        if self.vector_store.index.ntotal > 0 and not force_rebuild:
            log.info("RAG index already exists. Skipping rebuild.")
            return
            
        log.info(f"Building RAG index from {self.kb_dir}...")
        
        loader = DocumentLoader(self.kb_dir)
        documents = loader.load_all()
        if not documents:
            log.warning("No documents found to index.")
            return
            
        chunker = Chunker()
        chunks = chunker.chunk_documents(documents)
        
        texts = [c.text for c in chunks]
        embeddings = self.embedder.embed_texts(texts)
        
        # Reset index if force rebuild
        if force_rebuild:
            self.vector_store = VectorStoreManager(dimension=self.vector_store.dimension)
            self.retriever = Retriever(self.embedder, self.vector_store)
            
        self.vector_store.add_chunks(chunks, embeddings)
        self.vector_store.save_index(self.index_dir)
        log.info(f"Successfully indexed {len(chunks)} chunks.")
        
    def query(self, text: str, top_k: int = 3) -> RetrievalResponse:
        """Returns relevant context for the given text."""
        return self.retriever.retrieve(text, top_k=top_k)
