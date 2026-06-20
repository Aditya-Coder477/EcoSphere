import uuid
from typing import List
from .schemas import Document, Chunk

class Chunker:
    """Splits text into chunks by simple character count with overlap."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def chunk_document(self, document: Document) -> List[Chunk]:
        chunks = []
        text = document.text
        start = 0
        
        if not text:
            return chunks
            
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            chunks.append(Chunk(
                id=str(uuid.uuid4()),
                document_id=document.id,
                text=chunk_text,
                metadata=document.metadata
            ))
            
            if end >= len(text):
                break
            start += self.chunk_size - self.overlap
            
        return chunks
        
    def chunk_documents(self, documents: List[Document]) -> List[Chunk]:
        all_chunks = []
        for doc in documents:
            all_chunks.extend(self.chunk_document(doc))
        return all_chunks
