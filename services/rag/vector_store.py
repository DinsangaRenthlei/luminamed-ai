"""Qdrant vector store client."""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional
import uuid

from apps.api.app.config import get_settings
from services.rag.embeddings import get_embedder


settings = get_settings()


class MedicalKnowledgeStore:
    """Vector store for medical knowledge."""
    
    def __init__(self):
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection_name = settings.qdrant_collection
        self.embedder = get_embedder()
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedder.dimension,
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Created collection: {self.collection_name}")
    
    def add_knowledge(
        self,
        text: str,
        metadata: Dict,
        doc_id: Optional[str] = None
    ) -> str:
        """Add a knowledge document."""
        if doc_id is None:
            doc_id = str(uuid.uuid4())
        
        embedding = self.embedder.embed_text(text)
        
        point = PointStruct(
            id=doc_id,
            vector=embedding,
            payload={
                "text": text,
                **metadata
            }
        )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
        
        return doc_id
    
    def search(
        self,
        query: str,
        limit: int = 3,
        score_threshold: float = 0.5
    ) -> List[Dict]:
        """Search for relevant knowledge."""
        query_embedding = self.embedder.embed_text(query)
        
        # Use the correct API for qdrant-client 1.16.1
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=limit,
            score_threshold=score_threshold
        )
        
        # results is a QueryResponse object with .points attribute
        return [
            {
                "text": hit.payload["text"],
                "score": hit.score,
                **{k: v for k, v in hit.payload.items() if k != "text"}
            }
            for hit in results.points
        ]
    
    def count(self) -> int:
        """Get total number of documents."""
        return self.client.count(collection_name=self.collection_name).count


# Singleton
_store = None

def get_knowledge_store() -> MedicalKnowledgeStore:
    """Get knowledge store instance (cached)."""
    global _store
    if _store is None:
        _store = MedicalKnowledgeStore()
    return _store