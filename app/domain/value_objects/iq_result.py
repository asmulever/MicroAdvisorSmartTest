from dataclasses import dataclass


@dataclass(frozen=True)
class IqResult:
    """Resultado final del test IQ."""

    iq: int
    label: str
    score: float
    duration_sec: int
