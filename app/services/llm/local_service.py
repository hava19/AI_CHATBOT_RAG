from .base import BaseLLMService

class LocalLLMService(BaseLLMService):
    async def generate(self, prompt: str, **kwargs) -> str:
        return "Local model response"
    
    async def stream(self, prompt: str, **kwargs):
        yield "Local stream"
