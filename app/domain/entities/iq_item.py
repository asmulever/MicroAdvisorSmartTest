from dataclasses import dataclass
from typing import List, Optional, Any


@dataclass(frozen=True)
class IqItem:
    """Ítem del test IQ."""

    item_id: str
    domain: str
    difficulty: int
    prompt: str
    options: List[Any]
    correct: str
    visual: Optional[dict] = None
    difficulty_b: Optional[float] = None
    t_ref: Optional[float] = None
