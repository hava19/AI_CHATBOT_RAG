from .base import SQLBaseRepository

class UserRepository(SQLBaseRepository):
    async def get(self, id: str):
        return None
    
    async def create(self, entity):
        return entity
