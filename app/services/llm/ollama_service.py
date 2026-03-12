"""
Ollama LLM Service untuk FastAPI
Menggunakan Ollama API yang running di background
"""

import httpx
import json
from typing import AsyncGenerator, Optional
from app.core.config import settings
from .base import BaseLLMService

class OllamaService(BaseLLMService):
    """Service untuk berkomunikasi dengan Ollama"""
    
    def __init__(self):
        # Konfigurasi dari .env
        self.base_url = settings.OLLAMA_HOST or "http://localhost:11434"
        self.model = settings.OLLAMA_MODEL or "llama3.1:8b"
        self.timeout = 600
        
        # HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
        **kwargs
    ) -> str:
        """
        Generate response dari LLM (NON-STREAMING)
        """
        # Format prompt dengan system prompt jika ada
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Panggil Ollama API
        try:
            response = await self.client.post(
                "/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        **kwargs
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["message"]["content"]
            
        except httpx.TimeoutException:
            raise Exception(f"Ollama timeout setelah {self.timeout} detik")
        except httpx.HTTPStatusError as e:
            raise Exception(f"Ollama error: {e.response.text}")
        except Exception as e:
            raise Exception(f"Gagal komunikasi dengan Ollama: {str(e)}")
    
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream response dari LLM
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        async with self.client.stream(
            "POST",
            "/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    **kwargs
                }
            }
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "message" in data:
                            yield data["message"]["content"]
                        if data.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Alias untuk stream method (biar kompatibel)
        """
        async for chunk in self.stream(prompt, system_prompt, temperature, max_tokens, **kwargs):
            yield chunk
    
    async def close(self):
        """Cleanup HTTP client"""
        await self.client.aclose()