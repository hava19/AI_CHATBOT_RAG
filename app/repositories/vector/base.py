from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseVectorRepository(ABC):
    @abstractmethod
    async def upsert(self, id: str, vector: list, metadata: dict = None):
        pass
    
    @abstractmethod
    async def query(self, vector: list, top_k: int = 10):
        pass
