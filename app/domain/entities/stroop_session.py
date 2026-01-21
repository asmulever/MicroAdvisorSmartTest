from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class StroopTrial:
    """Trial de Stroop-WCST híbrido."""

    word: str
    ink: str
    trial_type: str  # congruente / incongruente / neutro
    rule_id: str
    expected: str


@dataclass
class StroopAnswer:
    """Respuesta a un trial de Stroop."""

    trial: StroopTrial
    selected: str
    correct: bool
    rt_ms: int
    rule_changed_before: bool


@dataclass
class StroopSession:
    """Sesión del test Stroop-WCST híbrido."""

    session_id: str
    current_rule: str
    total_trials: int = 0
    correct_in_rule: int = 0
    block_id: int = 1
    finished: bool = False
    answers: List[StroopAnswer] = field(default_factory=list)
