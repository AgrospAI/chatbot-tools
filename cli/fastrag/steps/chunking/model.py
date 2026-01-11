from typing import Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class Chunk:
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    parent_id: Optional[str] = None
    level: str = "child"