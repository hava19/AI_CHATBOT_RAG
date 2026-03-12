from dataclasses import dataclass
from uuid import UUID, uuid4
from typing import Optional, List

@dataclass
class Document:
    id: UUID = uuid4()
    content: str = ""
    metadata: dict = None
    embedding: Optional[List[float]] = None
