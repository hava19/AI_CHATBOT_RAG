from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

class BaseLLMService(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        pass
