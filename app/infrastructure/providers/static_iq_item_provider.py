from typing import Sequence

from app.application.ports.iq_repositories import IqItemProvider
from app.domain.entities.iq_item import IqItem
from app.iq_items import get_item_pool


class StaticIqItemProvider(IqItemProvider):
    """Proveedor estático de ítems IQ (Infrastructure)."""

    def get_pool(self) -> Sequence[IqItem]:
        return get_item_pool()
