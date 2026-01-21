import time
from dataclasses import asdict
from typing import Dict

from app.application.ports.iq_repositories import IqAnalyticsRepository, IqSessionRepository
from app.domain.exceptions import SessionNotFoundError
from app.domain.services.iq_logic import IqBandingService
from app.domain.services.iq_scoring_modes import IqScoringModesService
from app.domain.value_objects.iq_config import IqConfig


class FinishIqTestUseCase:
    """Caso de uso: finalizar test IQ."""

    def __init__(
        self,
        session_repo: IqSessionRepository,
        analytics_repo: IqAnalyticsRepository,
        banding_service: IqBandingService,
        scorer_modes: IqScoringModesService,
        config: IqConfig,
    ) -> None:
        self._session_repo = session_repo
        self._analytics_repo = analytics_repo
        self._banding_service = banding_service
        self._scorer_modes = scorer_modes
        self._config = config

    def execute(self, session_id: str) -> Dict:
        session = self._session_repo.get(session_id)
        if not session:
            raise SessionNotFoundError(session_id)

        if session.finished and session.result is not None:
            return session.result

        scores = self._scorer_modes.finalize_scores(session)
        session.score = scores["score"]
        iq_theta = scores["theta"]
        duration = int(time.time() - session.started_at)
        iq_value = max(70, min(145, int(round(100 + 15 * iq_theta))))
        label = self._banding_service.label(iq_value)
        band = self._banding_service.band(iq_value)
        self._analytics_repo.increment_finish(duration_sec=duration, band=band)

        session.result = {
            "iq": iq_value,
            "label": label,
            "score": round(session.score, 2),
            "duration_sec": duration,
        }
        session.finished = True
        self._session_repo.save(session)
        return session.result
