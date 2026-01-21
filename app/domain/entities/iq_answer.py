from dataclasses import dataclass


@dataclass(frozen=True)
class IqAnswer:
    """Respuesta entregada por el usuario para un ítem."""

    item_id: str
    answer: str
    timed_out: bool = False
    seconds: float = 0.0
    changes: int = 0
