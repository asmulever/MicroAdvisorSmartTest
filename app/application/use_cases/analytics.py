from typing import Dict, List

from app.application.ports.iq_repositories import IqAnalyticsRepository


class GetAnalyticsSummaryUseCase:
    """Caso de uso: resumen de analytics IQ."""

    def __init__(self, analytics_repo: IqAnalyticsRepository) -> None:
        self._analytics_repo = analytics_repo

    def execute(self, days: int) -> Dict:
        stats = self._analytics_repo.get_stats()
        finish_rate = (stats.finishes / stats.starts) if stats.starts else 0
        avg_time = (stats.total_time_sec / stats.finishes) if stats.finishes else 0
        return {
            "active_tests": 1,
            "finish_rate": round(finish_rate * 100, 1),
            "avg_time_sec": int(avg_time),
        }


class GetAnalyticsFunnelUseCase:
    """Caso de uso: funnel simple de IQ."""

    def __init__(self, analytics_repo: IqAnalyticsRepository) -> None:
        self._analytics_repo = analytics_repo

    def execute(self, days: int) -> Dict:
        stats = self._analytics_repo.get_stats()
        labels = ["Start", "Finish"]
        values = [stats.starts, stats.finishes]
        return {"labels": labels, "values": values}


class GetAnalyticsProfilesUseCase:
    """Caso de uso: distribución de perfiles IQ."""

    def __init__(self, analytics_repo: IqAnalyticsRepository) -> None:
        self._analytics_repo = analytics_repo

    def execute(self, days: int) -> Dict:
        stats = self._analytics_repo.get_stats()
        labels = list(stats.iq_bands.keys())
        values = [stats.iq_bands[label] for label in labels]
        return {"labels": labels, "values": values}


class GetAnalyticsDropoffUseCase:
    """Caso de uso: dropoff placeholder."""

    def execute(self, days: int) -> Dict:
        labels = [f"Q{i}" for i in range(1, 7)]
        values = [0 for _ in labels]
        return {"labels": labels, "values": values}
