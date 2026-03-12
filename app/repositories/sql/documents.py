from .base import SQLBaseRepository

class DocumentRepository(SQLBaseRepository):
    async def get(self, id: str):
        return None
    
    async def create(self, entity):
        return entity
