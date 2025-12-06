"""Embedding models for semantic search."""
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


class MedicalEmbedder:
    """Embedding model optimized for medical text."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize embedder."""
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def embed_text(self, text: str) -> List[float]:
        """Embed single text."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


# Singleton
_embedder = None

def get_embedder() -> MedicalEmbedder:
    """Get embedder instance (cached)."""
    global _embedder
    if _embedder is None:
        _embedder = MedicalEmbedder()
    return _embedder