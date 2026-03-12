from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Vector:
    values: List[float]
    metadata: dict = None
