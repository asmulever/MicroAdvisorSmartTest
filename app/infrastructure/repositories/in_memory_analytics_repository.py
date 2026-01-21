from app.application.ports.iq_repositories import IqAnalyticsRepository
from app.domain.entities.iq_analytics import IqAnalytics


class InMemoryIqAnalyticsRepository(IqAnalyticsRepository):
    """Repositorio en memoria de métricas IQ (Infrastructure)."""

    def __init__(self) -> None:
        self._stats = IqAnalytics()

    def increment_start(self) -> None:
        self._stats.starts += 1

    def increment_finish(self, duration_sec: int, band: str) -> None:
        self._stats.finishes += 1
        self._stats.total_time_sec += duration_sec
        if band not in self._stats.iq_bands:
            self._stats.iq_bands[band] = 0
        self._stats.iq_bands[band] += 1

    def get_stats(self) -> IqAnalytics:
        return self._stats
