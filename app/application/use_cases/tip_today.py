from typing import Dict

from app.application.ports.support_services import TipProvider


class GetTipTodayUseCase:
    """Caso de uso: consejo del día."""

    def __init__(self, tip_provider: TipProvider) -> None:
        self._tip_provider = tip_provider

    def execute(self) -> Dict:
        return self._tip_provider.get_tip()
