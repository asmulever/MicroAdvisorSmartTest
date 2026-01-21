from typing import Dict

from app.domain.services.stroop_engine import StroopEngine
from app.infrastructure.repositories.stroop_session_repository import InMemoryStroopSessionRepository


class AnswerStroopUseCase:
    """Procesa respuesta y entrega siguiente trial o fin."""

    def __init__(self, repo: InMemoryStroopSessionRepository, engine: StroopEngine) -> None:
        self._repo = repo
        self._engine = engine

    def execute(self, session_id: str, selected: str, rt_ms: int) -> Dict:
        session = self._repo.get(session_id)
        if not session:
            return {"error": "invalid_session"}, 400

        current_trial = self._repo.get_pending_trial(session_id)
        if not current_trial:
            return {"error": "no_trial"}, 400

        answer = self._engine.register_answer(session, current_trial, selected, rt_ms)
        next_trial = self._engine.next_trial(session)
        self._repo.set_pending_trial(session_id, next_trial)
        self._repo.save(session)

        payload = {
            "correct": answer.correct,
            "rule": session.current_rule,
            "finished": session.finished,
            "rt_ms": answer.rt_ms,
        }
        if next_trial and not session.finished:
            payload["next_trial"] = self._serialize_trial(next_trial)
        return payload, 200

    def _serialize_trial(self, trial):
        return {
            "word": trial.word,
            "ink": trial.ink,
            "trial_type": trial.trial_type,
            "rule_id": trial.rule_id,
        }
