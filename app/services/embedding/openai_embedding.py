from .base import BaseEmbeddingService
from typing import List

class OpenAIEmbeddingService(BaseEmbeddingService):
    async def embed(self, text: str) -> List[float]:
        return [0.1] * 1536
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * 1536 for _ in texts]
