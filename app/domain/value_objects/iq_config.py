from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class IqConfig:
    """Configuración base del test IQ (dominio IQ)."""

    n_items: int
    score_max: float
    difficulty_weights: Dict[int, float]
    time_limits: Dict[int, int]
