from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import List

@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime

@dataclass
class Conversation:
    id: UUID
    user_id: UUID
    messages: List[Message]
    created_at: datetime
