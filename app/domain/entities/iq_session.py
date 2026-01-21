from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class IqSession:
    """Sesión de IQ en curso."""

    session_id: str
    started_at: float
    difficulty: int
    score: float
    answers_count: int
    used_items: List[str]
    n_items: int
    block_size: int
    scoring_mode: int
    theta: float = 0.0
    simple_corrects: int = 0
    weighted_sum: float = 0.0
    weighted_total: float = 0.0
    finished: bool = False
    result: Optional[dict] = None
