from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class MixedItem:
    """Item combinado IQ + Stroop."""

    item_id: str
    kind: str  # iq | stroop
    payload: Dict


@dataclass
class MixedSession:
    """Sesión de test combinado."""

    session_id: str
    items: List[MixedItem] = field(default_factory=list)
    index: int = 0
    iq_correct: int = 0
    iq_total: int = 0
    stroop_correct: int = 0
    stroop_total: int = 0
    finished: bool = False
