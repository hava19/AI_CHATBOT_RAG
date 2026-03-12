from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def get(self, id: str) -> T:
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass
