from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List
from .chat import ChatMessage

class ConversationResponse(BaseModel):
    id: UUID
    messages: List[ChatMessage]
    created_at: datetime
