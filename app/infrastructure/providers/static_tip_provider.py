from app.application.ports.support_services import TipProvider


class StaticTipProvider(TipProvider):
    """Proveedor estático de consejos (Infrastructure)."""

    def get_tip(self) -> dict:
        # MVP: hardcodeado. Extensible a repositorio/servicio externo.
        return {
            "date": "today",
            "title": "Consejo del día",
            "tip": "Antes de comprar, esperá 10 minutos. Reduce compras impulsivas.",
        }
