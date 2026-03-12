"""
Embedding service menggunakan sentence-transformers
Untuk mengubah teks menjadi vector
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.core.config import settings

class SentenceTransformerService:
    def __init__(self):
        # Load model embedding (download otomatis pertama kali)
        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL,
            cache_folder="models/embedding"
        )
    
    async def embed(self, text: str) -> List[float]:
        """
        Embed single text
        """
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed batch of texts
        """
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
    
    def embed_sync(self, text: str) -> List[float]:
        """
        Sync version untuk background task
        """
        embedding = self.model.encode(text)
        return embedding.tolist()

# Singleton instance
embedding_service = SentenceTransformerService()