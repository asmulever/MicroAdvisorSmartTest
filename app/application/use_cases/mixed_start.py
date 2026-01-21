import uuid
from typing import Dict

from app.domain.services.mixed_engine import MixedEngine
from app.infrastructure.repositories.mixed_session_repository import InMemoryMixedSessionRepository


class StartMixedUseCase:
    """Inicia test combinado IQ + Stroop."""

    def __init__(self, repo: InMemoryMixedSessionRepository, engine: MixedEngine) -> None:
        self._repo = repo
        self._engine = engine

    def execute(self, iq_count: int = 10, stroop_count: int = 6) -> Dict:
        session_id = str(uuid.uuid4())
        session = self._engine.build_session(session_id, iq_count=iq_count, stroop_count=stroop_count)
        item = self._engine.next_item(session)
        self._repo.save(session)
        return {"session_id": session_id, "item": self._serialize(item)}

    def _serialize(self, item):
        return {
            "item_id": item.item_id,
            "kind": item.kind,
            "payload": item.payload,
        }
