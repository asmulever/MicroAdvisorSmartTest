from typing import Dict, Optional

from app.domain.entities.mixed_session import MixedSession


class InMemoryMixedSessionRepository:
    """Repositorio en memoria para sesiones combinadas."""

    def __init__(self) -> None:
        self._sessions: Dict[str, MixedSession] = {}

    def save(self, session: MixedSession) -> None:
        self._sessions[session.session_id] = session

    def get(self, session_id: str) -> Optional[MixedSession]:
        return self._sessions.get(session_id)
