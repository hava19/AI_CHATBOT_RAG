from .base import BaseVectorRepository

class WeaviateRepository(BaseVectorRepository):
    async def upsert(self, id: str, vector: list, metadata: dict = None):
        pass
    
    async def query(self, vector: list, top_k: int = 10):
        return []
