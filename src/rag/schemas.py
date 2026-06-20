from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DocumentMetadata(BaseModel):
    source: str
    doc_type: str
    year: Optional[int] = None
    category: Optional[str] = None
    country: Optional[str] = None

class Document(BaseModel):
    id: str
    text: str
    metadata: DocumentMetadata

class Chunk(BaseModel):
    id: str
    document_id: str
    text: str
    metadata: DocumentMetadata

class RetrievalResult(BaseModel):
    chunk: Chunk
    score: float

class RetrievalResponse(BaseModel):
    results: List[RetrievalResult]
    relevance: bool
    weak_context: bool
