from dataclasses import dataclass
from uuid import UUID

@dataclass
class Chunk:
    id: UUID
    document_id: UUID
    content: str
    index: int
    embedding: list = None
