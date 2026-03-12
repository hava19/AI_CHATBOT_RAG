from .base import BaseLLMService
import openai
from typing import AsyncGenerator

class OpenAIService(BaseLLMService):
    async def generate(self, prompt: str, **kwargs) -> str:
        # Implementasi OpenAI
        return "OpenAI response"
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        yield "Streaming response"
