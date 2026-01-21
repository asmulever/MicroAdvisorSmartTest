from typing import Protocol


class TipProvider(Protocol):
    """Puerto para consejo del día."""

    def get_tip(self) -> dict:
        ...


class DbHealthChecker(Protocol):
    """Puerto para verificar conectividad a BD."""

    def check(self) -> bool:
        ...
