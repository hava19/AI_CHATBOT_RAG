from .base import BaseLLMService

class AnthropicService(BaseLLMService):
    async def generate(self, prompt: str, **kwargs) -> str:
        return "Anthropic response"
    
    async def stream(self, prompt: str, **kwargs):
        yield "Anthropic stream"
