from typing import Dict

from app.domain.services.mixed_engine import MixedEngine
from app.infrastructure.repositories.mixed_session_repository import InMemoryMixedSessionRepository


class AnswerMixedUseCase:
    """Procesa respuesta y entrega siguiente ítem o fin."""

    def __init__(self, repo: InMemoryMixedSessionRepository, engine: MixedEngine) -> None:
        self._repo = repo
        self._engine = engine

    def execute(self, session_id: str, answer: str) -> Dict:
        session = self._repo.get(session_id)
        if not session:
            return {"error": "invalid_session"}, 400
        current = self._engine.next_item(session)
        if not current:
            return {"error": "no_item"}, 400
        correct = self._engine.register_answer(session, current, answer)
        next_item = self._engine.next_item(session)
        self._repo.save(session)
        resp = {"correct": correct, "finished": session.finished}
        if next_item and not session.finished:
            resp["item"] = {"item_id": next_item.item_id, "kind": next_item.kind, "payload": next_item.payload}
        return resp, 200
