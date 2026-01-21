from dataclasses import dataclass, field
from typing import Dict


@dataclass
class IqAnalytics:
    """Estadísticas agregadas del test IQ."""

    starts: int = 0
    finishes: int = 0
    total_time_sec: int = 0
    iq_bands: Dict[str, int] = field(default_factory=lambda: {
        "<90": 0,
        "90-109": 0,
        "110-119": 0,
        "120-129": 0,
        ">=130": 0,
    })
