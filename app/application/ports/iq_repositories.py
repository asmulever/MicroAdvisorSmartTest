from typing import Optional, Protocol, Sequence

from app.domain.entities.iq_analytics import IqAnalytics
from app.domain.entities.iq_item import IqItem
from app.domain.entities.iq_session import IqSession


class IqSessionRepository(Protocol):
    """Puerto para persistir sesiones IQ."""

    def save(self, session: IqSession) -> None:
        ...

    def get(self, session_id: str) -> Optional[IqSession]:
        ...


class IqAnalyticsRepository(Protocol):
    """Puerto para métricas de IQ."""

    def increment_start(self) -> None:
        ...

    def increment_finish(self, duration_sec: int, band: str) -> None:
        ...

    def get_stats(self) -> IqAnalytics:
        ...


class IqItemProvider(Protocol):
    """Puerto para obtener pool de ítems IQ."""

    def get_pool(self) -> Sequence[IqItem]:
        ...
