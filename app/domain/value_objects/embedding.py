from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Embedding:
    vector: List[float]
    model: str
    
    def __len__(self):
        return len(self.vector)
