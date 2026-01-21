import uuid
from typing import Dict

from app.domain.services.stroop_engine import StroopEngine
from app.infrastructure.repositories.stroop_session_repository import InMemoryStroopSessionRepository


class StartStroopUseCase:
    """Inicia sesión del test Stroop-WCST híbrido."""

    def __init__(self, repo: InMemoryStroopSessionRepository, engine: StroopEngine) -> None:
        self._repo = repo
        self._engine = engine

    def execute(self) -> Dict:
        session_id = str(uuid.uuid4())
        session, trial = self._engine.start_session(session_id)
        self._repo.save(session)
        return {"session_id": session_id, "trial": self._serialize_trial(trial), "rule_hint": "descubre la regla por aciertos"}

    def _serialize_trial(self, trial):
        return {
            "word": trial.word,
            "ink": trial.ink,
            "trial_type": trial.trial_type,
            "rule_id": trial.rule_id,
        }
