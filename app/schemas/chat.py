from pydantic import BaseModel
from typing import Optional, List, Any

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512
    use_rag: Optional[bool] = True  # Bisa matikan RAG kalau mau

class ChatResponse(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    sources: Optional[List[Any]] = None  # Sumber dokumen