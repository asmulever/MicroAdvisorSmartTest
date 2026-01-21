from typing import Dict

from app.domain.services.mixed_engine import MixedEngine
from app.infrastructure.repositories.mixed_session_repository import InMemoryMixedSessionRepository


class FinishMixedUseCase:
    """Finaliza test combinado y retorna score."""

    def __init__(self, repo: InMemoryMixedSessionRepository, engine: MixedEngine) -> None:
        self._repo = repo
        self._engine = engine

    def execute(self, session_id: str) -> Dict:
        session = self._repo.get(session_id)
        if not session:
            return {"error": "invalid_session"}, 400
        session.finished = True
        score = self._engine.finalize(session)
        self._repo.save(session)
        return score, 200
