import os
import uuid
from pathlib import Path
from typing import List
from .schemas import Document, DocumentMetadata
from .exceptions import DocumentLoadError

class DocumentLoader:
    """Loads documents from a local directory."""
    
    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        
    def load_all(self) -> List[Document]:
        if not self.directory.exists():
            raise DocumentLoadError(f"Directory {self.directory} does not exist.")
            
        docs = []
        for file_path in self.directory.glob("**/*"):
            if file_path.is_file() and file_path.suffix in [".txt", ".md"]:
                docs.append(self.load_file(file_path))
        return docs
        
    def load_file(self, file_path: Path) -> Document:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Basic metadata extraction from path or defaults
            metadata = DocumentMetadata(
                source=file_path.name,
                doc_type=file_path.suffix.lstrip("."),
                category=file_path.parent.name if file_path.parent != self.directory else "general"
            )
            
            return Document(
                id=str(uuid.uuid4()),
                text=content,
                metadata=metadata
            )
        except Exception as e:
            raise DocumentLoadError(f"Failed to load {file_path}: {e}")
